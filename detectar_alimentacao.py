from ultralytics import YOLO
import cv2
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

from dashboard_alertas.servico_alertas import aplicar_alertas


# --- Entrada: webcam ou arquivo ---
# True  = usa a câmera ao vivo (0 = webcam padrão; se não abrir, tente INDICE_CAMERA = 1)
# False = usa o arquivo de vídeo em VIDEO
USAR_WEBCAM = False
INDICE_CAMERA = 0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_EXEMPLOS = os.path.join(BASE_DIR, "exemplos")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "dashboard_alertas", "relatorios")

VIDEO = os.environ.get("VIDEO_NOME", r"one_cat_eating.mp4")
VIDEO_BASE = os.path.splitext(os.path.basename(VIDEO))[0]
SAIDA = os.path.join(BASE_DIR, f"alimentacao_resultado_{VIDEO_BASE}.mp4")

CLASSE_PETS    = [15, 16]
CLASSE_TIGELA = 45

EXPANSAO_TIGELA = 1.8
TEMPO_MIN       = 5
TOLERANCIA_PAUSA = 2

# Variáveis dos estados
comendo_agora    = False
inicio_refeicao  = None
ultima_refeicao  = None
saiu_em          = None
eventos          = []
cheiradas        = []
ultimo_status    = "aguardando"


def listar_videos_exemplos():
    extensoes = (".mp4", ".avi", ".mov", ".mkv")
    if not os.path.isdir(PASTA_EXEMPLOS):
        return []
    return sorted(
        nome for nome in os.listdir(PASTA_EXEMPLOS)
        if nome.lower().endswith(extensoes)
    )


def resolver_video(nome_ou_caminho):
    """Procura o vídeo na raiz do projeto ou na pasta exemplos/."""
    if os.path.isabs(nome_ou_caminho) and os.path.isfile(nome_ou_caminho):
        return nome_ou_caminho

    na_raiz = os.path.join(BASE_DIR, nome_ou_caminho)
    if os.path.isfile(na_raiz):
        return na_raiz

    em_exemplos = os.path.join(PASTA_EXEMPLOS, os.path.basename(nome_ou_caminho))
    if os.path.isfile(em_exemplos):
        return em_exemplos

    return nome_ou_caminho


def caminho_relativo(caminho_abs):
    try:
        return os.path.relpath(caminho_abs, BASE_DIR).replace("\\", "/")
    except ValueError:
        return caminho_abs


def processar_todos_os_videos():
    videos = listar_videos_exemplos()
    if not videos:
        print("ERRO: nenhum vídeo encontrado na pasta exemplos/.")
        sys.exit(1)

    print(f"Processando {len(videos)} vídeo(s) da pasta exemplos/...\n")
    for indice, video in enumerate(videos, 1):
        print(f"=== Vídeo {indice}/{len(videos)}: {video} ===")
        env = os.environ.copy()
        env["PROCESSAR_UM_VIDEO"] = "1"
        env["SEM_PAUSA"] = "1"
        env["VIDEO_NOME"] = video
        subprocess.run([sys.executable, os.path.abspath(__file__)], cwd=BASE_DIR, env=env, check=False)

    print("\nProcessamento finalizado.")
    print(f"Relatórios salvos em: {PASTA_RELATORIOS}")


def animal_perto_tigela(animal_bbox, tigela_bbox):
    cx = (tigela_bbox[0] + tigela_bbox[2]) / 2
    cy = (tigela_bbox[1] + tigela_bbox[3]) / 2
    w  = (tigela_bbox[2] - tigela_bbox[0]) * EXPANSAO_TIGELA
    h  = (tigela_bbox[3] - tigela_bbox[1]) * EXPANSAO_TIGELA
    t = [cx - w/2, cy - h/2, cx + w/2, cy + h/2]

    return (animal_bbox[0] < t[2] and animal_bbox[2] > t[0] and
            animal_bbox[1] < t[3] and animal_bbox[3] > t[1])


if __name__ == "__main__" and os.environ.get("PROCESSAR_UM_VIDEO") != "1":
    processar_todos_os_videos()
    sys.exit(0)


cv2.destroyAllWindows()

model = YOLO(os.path.join(BASE_DIR, "yolov8s.pt"))

if USAR_WEBCAM:
    # No Windows, DirectShow costuma abrir a webcam mais rápido
    if os.name == "nt":
        cap = cv2.VideoCapture(INDICE_CAMERA, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(INDICE_CAMERA)
    origem_relatorio = f"webcam:{INDICE_CAMERA}"
else:
    VIDEO = resolver_video(VIDEO)
    cap = cv2.VideoCapture(VIDEO)
    origem_relatorio = caminho_relativo(VIDEO)

if not cap.isOpened():
    print("ERRO: não abriu a fonte de vídeo.")
    if USAR_WEBCAM:
        print(f"  Webcam índice {INDICE_CAMERA}. Tente INDICE_CAMERA = 1 (USB) ou verifique permissões.")
    else:
        print(f"  Arquivo: {VIDEO}")
    raise SystemExit(1)

fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(SAIDA, cv2.VideoWriter_fourcc(*"mp4v"), fps, (largura, altura))

inicio_video = datetime.now()
frame_n = 0

print("Monitorando......." + (" [WEBCAM]" if USAR_WEBCAM else f" [{VIDEO}]"))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_n += 1
    agora = inicio_video + timedelta(seconds=frame_n / fps)

    # Detectar cão/gato e tigela no frame
    resultado = model.predict(frame, classes=CLASSE_PETS + [CLASSE_TIGELA],
                               conf=0.15, verbose=False)

    tigelas = []
    cao_detectado = False
    cao_bbox = None

    if resultado[0].boxes is not None:
        for box in resultado[0].boxes:
            cls  = int(box.cls[0])
            bbox = box.xyxy[0].cpu().numpy().astype(int).tolist()
            conf = float(box.conf[0])

            if cls == CLASSE_TIGELA:
                tigelas.append(bbox)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 165, 0), 2)
                cv2.putText(frame, f"Tigela {conf:.0%}", (bbox[0], bbox[1]-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)

            elif cls in CLASSE_PETS:
                cao_detectado = True
                cao_bbox = bbox
                nome = model.names[cls]
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                cv2.putText(frame, f"{nome} {conf:.0%}", (bbox[0], bbox[1]-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Lógica de se está comendo ou não
    perto = False
    if cao_detectado and tigelas:
        for t in tigelas:
            if animal_perto_tigela(cao_bbox, t):
                perto = True
                break

    if perto:
        saiu_em = None
        if not comendo_agora:
            comendo_agora = True
            if inicio_refeicao is None:
                inicio_refeicao = agora

    else:
        if comendo_agora:
            if saiu_em is None:
                saiu_em = agora

            pausa = (agora - saiu_em).total_seconds()
            if pausa > TOLERANCIA_PAUSA:
                duracao = (saiu_em - inicio_refeicao).total_seconds()
                comendo_agora = False
                inicio_refeicao = None
                saiu_em = None

                if duracao >= TEMPO_MIN:
                    ultima_refeicao = agora
                    eventos.append({
                        "tipo": "refeicao",
                        "inicio": (agora - timedelta(seconds=duracao)).strftime("%H:%M:%S"),
                        "duracao_s": round(duracao, 1),
                    })
                    print(f"  Refeição confirmada: {duracao:.1f}s")
                else:
                    # Interação curta = cheirando (conforme regras)
                    cheiradas.append({
                        "horario": (agora - timedelta(seconds=duracao)).strftime("%H:%M:%S"),
                        "duracao_s": round(duracao, 1),
                    })
                    ultimo_status = "cheirando"
                    print(f"  Cheirando detectado: {duracao:.1f}s")

    # Legendas no vídeo
    ref = ultima_refeicao or inicio_video
    apatico = (agora - ref).total_seconds() > 2 * 3600

    if comendo_agora and inicio_refeicao:
        tempo_comendo = (agora - inicio_refeicao).total_seconds()
        status_txt = f"COMENDO  {tempo_comendo:.0f}s"
        status_cor = (0, 200, 0)
        sem_txt    = "Comendo agora!"
        sem_cor    = (0, 200, 0)
        ultimo_status = "comendo"
    elif ultimo_status == "cheirando":
        status_txt = "CHEIRANDO"
        status_cor = (0, 200, 255)
        sem_txt    = "Aproximacao curta detectada"
        sem_cor    = (0, 200, 255)
        ultimo_status = "aguardando"
    else:
        status_txt = "APATICO" if apatico else "aguardando"
        status_cor = (0, 0, 255) if apatico else (180, 180, 180)
        if ultima_refeicao:
            sem_comer = (agora - ultima_refeicao).total_seconds()
            sem_txt   = f"Sem comer: {sem_comer/60:.1f} min"
            sem_cor   = (0, 0, 255) if sem_comer > 6 * 3600 else (200, 200, 200)
        else:
            sem_txt = "Sem comer: aguardando a refeicao"
            sem_cor = (200, 200, 200)

    cv2.rectangle(frame, (0, 0), (380, 70), (20, 20, 20), -1)
    cv2.putText(frame, status_txt, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_cor, 2)
    cv2.putText(frame, sem_txt,    (10, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, sem_cor, 1)

    out.write(frame)
    cv2.imshow("Monitorando Alimentacao", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()

if comendo_agora and inicio_refeicao:
    duracao = (agora - inicio_refeicao).total_seconds()
    if duracao >= TEMPO_MIN:
        eventos.append({
            "tipo": "refeicao",
            "inicio": inicio_refeicao.strftime("%H:%M:%S"),
            "duracao_s": round(duracao, 1),
        })

out.release()
cv2.destroyAllWindows()

# Relatório final

print("\n=== RELATÓRIO ===")
print(f"Refeições confirmadas : {len(eventos)}")
for i, e in enumerate(eventos, 1):
    print(f"  {i}. {e['inicio']}  —  {e['duracao_s']}s")
print(f"Cheiradas detectadas  : {len(cheiradas)}")
for i, c in enumerate(cheiradas, 1):
    print(f"  {i}. {c['horario']}  —  {c['duracao_s']}s")

relatorio = {
    "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data": datetime.now().strftime("%Y-%m-%d"),
    "horario_inicio": inicio_video.strftime("%H:%M:%S"),
    "horario_fim": datetime.now().strftime("%H:%M:%S"),
    "video_analisado": origem_relatorio,
    "refeicoes_confirmadas": len(eventos),
    "refeicoes": eventos,
    "cheiradas": cheiradas,
    "alertas": []
}

relatorio = aplicar_alertas(relatorio, {}, eventos, datetime.now())

os.makedirs(PASTA_RELATORIOS, exist_ok=True)
nome_arquivo = os.path.join(
    PASTA_RELATORIOS,
    f"relatorio_{VIDEO_BASE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
)
with open(nome_arquivo, "w", encoding="utf-8") as f:
    json.dump(relatorio, f, ensure_ascii=False, indent=2)

print(f"\nVídeo salvo  : {SAIDA}")
print(f"Relatório    : {nome_arquivo}")

if os.environ.get("SEM_PAUSA") != "1":
    input("\nPressione Enter para fechar...")
