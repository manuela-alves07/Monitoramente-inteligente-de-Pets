from ultralytics import YOLO
import cv2
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta

VIDEO      = sys.argv[1] if len(sys.argv) > 1 else "exemplos/one_cat_eating.mp4"
SAIDA      = "alimentacao_resultado.mp4"
MODO_API   = len(sys.argv) > 1

CLASSE_PETS    = [15, 16]
CLASSE_TIGELA  = 45

DIST_MAX         = 1.5
TEMPO_MIN        = 5
TEMPO_BEBER_MIN  = 3
TOLERANCIA_PAUSA = 2
PROCESSAR_A_CADA = 5


def centro(bbox):
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

def dist_normalizada(animal_bbox, tigela_bbox):
    ax, ay = centro(animal_bbox)
    tx, ty = centro(tigela_bbox)
    dist = ((ax - tx) ** 2 + (ay - ty) ** 2) ** 0.5
    largura = max(animal_bbox[2] - animal_bbox[0], 1)
    return dist / largura

def calc_movimento(hist):
    if len(hist) < 5:
        return 0
    dists = [((hist[i][0] - hist[i-1][0]) ** 2 + (hist[i][1] - hist[i-1][1]) ** 2) ** 0.5
             for i in range(1, len(hist))]
    return np.mean(dists)

def perto_de_tigela(animal_bbox, tigelas):
    return any(dist_normalizada(animal_bbox, t) < DIST_MAX for t in tigelas)


model = YOLO("yolov8s.pt")

cap     = cv2.VideoCapture(VIDEO)
fps     = cap.get(cv2.CAP_PROP_FPS) or 30.0
largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
altura  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(SAIDA, cv2.VideoWriter_fourcc(*"mp4v"), fps, (largura, altura))

inicio_video = datetime.now()
frame_n      = 0
agora        = inicio_video

animais   = {}
eventos   = []
cheiradas = []

print("Monitorando.......")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_n += 1
    agora = inicio_video + timedelta(seconds=frame_n / fps)

    if frame_n % PROCESSAR_A_CADA != 0:
        out.write(frame)
        continue

    results = model.track(frame, persist=True,
                          classes=CLASSE_PETS + [CLASSE_TIGELA],
                          conf=0.15, verbose=False)

    tigelas = []

    if results[0].boxes is not None:
        for box in results[0].boxes:
            cls  = int(box.cls[0])
            bbox = box.xyxy[0].cpu().numpy().astype(int).tolist()
            conf = float(box.conf[0])

            if cls == CLASSE_TIGELA:
                tigelas.append(bbox)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 165, 0), 2)
                cv2.putText(frame, f"Tigela {conf:.0%}", (bbox[0], bbox[1] - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)

        for box in results[0].boxes:
            cls  = int(box.cls[0])
            bbox = box.xyxy[0].cpu().numpy().astype(int).tolist()
            conf = float(box.conf[0])

            if cls not in CLASSE_PETS or box.id is None:
                continue

            track_id = int(box.id[0])

            if track_id not in animais:
                animais[track_id] = {
                    "hist":           [],
                    "comendo_agora":  False,
                    "inicio_refeicao": None,
                    "saiu_em":        None,
                    "ultima_refeicao": None,
                    "ultimo_status":  "aguardando",
                    "estado":         "aguardando",
                }

            a = animais[track_id]

            cx, cy = centro(bbox)
            a["hist"].append((cx, cy))
            if len(a["hist"]) > 20:
                a["hist"].pop(0)

            movimento = calc_movimento(a["hist"])
            perto     = perto_de_tigela(bbox, tigelas)

            if perto:
                a["saiu_em"] = None
                if not a["comendo_agora"]:
                    a["comendo_agora"]   = True
                    a["inicio_refeicao"] = a["inicio_refeicao"] or agora
            else:
                if a["comendo_agora"]:
                    if a["saiu_em"] is None:
                        a["saiu_em"] = agora
                    pausa = (agora - a["saiu_em"]).total_seconds()
                    if pausa > TOLERANCIA_PAUSA:
                        duracao = (a["saiu_em"] - a["inicio_refeicao"]).total_seconds()
                        a["comendo_agora"]   = False
                        a["inicio_refeicao"] = None
                        a["saiu_em"]         = None

                        if duracao >= TEMPO_MIN:
                            a["ultima_refeicao"] = agora
                            a["ultimo_status"]   = "comendo"
                            eventos.append({
                                "tipo":      "refeicao",
                                "animal_id": track_id,
                                "inicio":    (agora - timedelta(seconds=duracao)).strftime("%H:%M:%S"),
                                "duracao_s": round(duracao, 1),
                            })
                            print(f"  Refeição confirmada (ID {track_id}): {duracao:.1f}s")
                        else:
                            a["ultimo_status"] = "cheirando"
                            cheiradas.append({
                                "animal_id": track_id,
                                "horario":   (agora - timedelta(seconds=duracao)).strftime("%H:%M:%S"),
                                "duracao_s": round(duracao, 1),
                            })
                            print(f"  Cheirando (ID {track_id}): {duracao:.1f}s")

            if a["comendo_agora"] and a["inicio_refeicao"]:
                tempo_perto = (agora - a["inicio_refeicao"]).total_seconds()
                if movimento < 1.5 and tempo_perto > TEMPO_BEBER_MIN:
                    estado = "BEBENDO"
                    cor    = (255, 100, 0)
                else:
                    estado = "COMENDO"
                    cor    = (0, 200, 0)
            elif a["ultimo_status"] == "cheirando":
                estado             = "CHEIRANDO"
                cor                = (0, 200, 255)
                a["ultimo_status"] = "aguardando"
            else:
                ref     = a["ultima_refeicao"] or inicio_video
                apatico = (agora - ref).total_seconds() > 2 * 3600
                estado  = "APATICO" if apatico else "aguardando"
                cor     = (0, 0, 255) if apatico else (180, 180, 180)

            a["estado"] = estado

            nome = model.names[cls]
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), cor, 2)
            cv2.putText(frame, f"{nome} #{track_id}  {estado}  {conf:.0%}",
                        (bbox[0], bbox[1] - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, cor, 1)

    a = next(iter(animais.values())) if animais else None
    if True:
        if a and a["comendo_agora"] and a["inicio_refeicao"]:
            tempo_comendo = (agora - a["inicio_refeicao"]).total_seconds()
            status_txt = f"COMENDO  {tempo_comendo:.0f}s"
            status_cor = (0, 200, 0)
            sem_txt    = "Comendo agora!"
            sem_cor    = (0, 200, 0)
        elif a and a["ultimo_status"] == "cheirando":
            status_txt = "CHEIRANDO"
            status_cor = (0, 200, 255)
            sem_txt    = "Aproximacao curta detectada"
            sem_cor    = (0, 200, 255)
        elif a:
            ref     = a["ultima_refeicao"] or inicio_video
            apatico = (agora - ref).total_seconds() > 2 * 3600
            status_txt = "APATICO" if apatico else "aguardando"
            status_cor = (0, 0, 255) if apatico else (180, 180, 180)
            if a["ultima_refeicao"]:
                sem_comer = (agora - a["ultima_refeicao"]).total_seconds()
                sem_txt   = f"Sem comer: {sem_comer/60:.1f} min"
                sem_cor   = (0, 0, 255) if sem_comer > 6 * 3600 else (200, 200, 200)
            else:
                sem_txt = "Sem comer: aguardando a refeicao"
                sem_cor = (200, 200, 200)
        else:
            status_txt = "aguardando"
            status_cor = (180, 180, 180)
            sem_txt    = "Nenhum animal detectado"
            sem_cor    = (180, 180, 180)
        cv2.rectangle(frame, (0, 0), (380, 70), (20, 20, 20), -1)
        cv2.putText(frame, status_txt, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_cor, 2)
        cv2.putText(frame, sem_txt, (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, sem_cor, 1)

    out.write(frame)
    if not MODO_API:
        cv2.imshow("Monitorando Alimentacao", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()

for track_id, a in animais.items():
    if a["comendo_agora"] and a["inicio_refeicao"]:
        duracao = (agora - a["inicio_refeicao"]).total_seconds()
        if duracao >= TEMPO_MIN:
            eventos.append({
                "tipo":      "refeicao",
                "animal_id": track_id,
                "inicio":    a["inicio_refeicao"].strftime("%H:%M:%S"),
                "duracao_s": round(duracao, 1),
            })

out.release()
if not MODO_API:
    cv2.destroyAllWindows()

print("\n=== RELATÓRIO ===")
print(f"Refeições confirmadas : {len(eventos)}")
for i, e in enumerate(eventos, 1):
    print(f"  {i}. Animal #{e['animal_id']}  {e['inicio']}  —  {e['duracao_s']}s")
print(f"Cheiradas detectadas  : {len(cheiradas)}")
for i, c in enumerate(cheiradas, 1):
    print(f"  {i}. Animal #{c['animal_id']}  {c['horario']}  —  {c['duracao_s']}s")

relatorio = {
    "gerado_em":             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data":                  datetime.now().strftime("%Y-%m-%d"),
    "horario_inicio":        inicio_video.strftime("%H:%M:%S"),
    "horario_fim":           datetime.now().strftime("%H:%M:%S"),
    "video_analisado":       VIDEO,
    "refeicoes_confirmadas": len(eventos),
    "refeicoes":             eventos,
    "cheiradas":             cheiradas,
    "alertas":               [],
}

for track_id, a in animais.items():
    if a["ultima_refeicao"]:
        sem_comer = (datetime.now() - a["ultima_refeicao"]).total_seconds()
        if sem_comer > 6 * 3600:
            relatorio["alertas"].append({
                "tipo":      "sem_alimentacao",
                "animal_id": track_id,
                "mensagem":  f"Animal #{track_id} sem comer ha {sem_comer/3600:.1f}h",
                "nivel":     "critico",
            })

if not eventos:
    relatorio["alertas"].append({
        "tipo":     "sem_refeicao_detectada",
        "mensagem": "Nenhuma refeicao confirmada no periodo",
        "nivel":    "aviso",
    })

if MODO_API:
    print("===RELATORIO_JSON===")
    print(json.dumps(relatorio, ensure_ascii=False))
else:
    os.makedirs("relatorios", exist_ok=True)
    nome_arquivo = f"relatorios/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    print(f"\nVídeo salvo  : {SAIDA}")
    print(f"Relatório    : {nome_arquivo}")
    input("\nPressione Enter para fechar...")
