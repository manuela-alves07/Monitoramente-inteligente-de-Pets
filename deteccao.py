"""
VetVision – Monitoramento Veterinário com IA
Módulo: Detecção YOLO via Roboflow (versão Colab)

Como usar no Google Colab:
    1. Suba este arquivo no Colab
    2. Rode: !python rafa_deteccao_colab.py
    OU copie o conteúdo em células do notebook
"""

# PASSO 1 — Instalar dependências
import subprocess
subprocess.run(["pip", "install", "opencv-python-headless", "requests", "-q"])

# PASSO 2 — Fazer upload do vídeo
from google.colab import files
uploaded = files.upload()
nome_video = list(uploaded.keys())[0]
print(f'Vídeo carregado: {nome_video}')

# PASSO 3 — Rodar a detecção e salvar o vídeo anotado
import cv2
import base64
import requests

ROBOFLOW_API_KEY = 'NNRaoXh6QTL5y7mXASsa'
ROBOFLOW_MODEL   = 'pi-liqod/3'
ROBOFLOW_URL     = f'https://serverless.roboflow.com/{ROBOFLOW_MODEL}'

CLASSES_ALVO     = {'dog', 'cat', 'bowl'}
CONFIANCA_MINIMA = 0.75
PROCESSAR_A_CADA = 5

CORES = {
    'cat':  (0, 200, 255),
    'dog':  (50, 220, 50),
    'bowl': (255, 80, 80),
}

def detectar_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    try:
        resp = requests.post(
            ROBOFLOW_URL,
            params={'api_key': ROBOFLOW_API_KEY},
            data=img_b64,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=5,
        )
        return resp.json().get('predictions', [])
    except Exception as e:
        print(f'[ERRO] {e}')
        return []

def desenhar(frame, preds):
    for pred in preds:
        classe = pred.get('class', '')
        if classe not in CLASSES_ALVO:
            continue
        conf = float(pred.get('confidence', 0))
        if conf < CONFIANCA_MINIMA:
            continue
        cx, cy = pred['x'], pred['y']
        w,  h  = pred['width'], pred['height']
        x1, y1 = int(cx - w/2), int(cy - h/2)
        x2, y2 = int(cx + w/2), int(cy + h/2)
        cor   = CORES.get(classe, (200, 200, 200))
        label = f'{classe} {conf:.0%}'
        cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1-lh-8), (x1+lw+4, y1), cor, -1)
        cv2.putText(frame, label, (x1+2, y1-4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame

cap   = cv2.VideoCapture(nome_video)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps   = cap.get(cv2.CAP_PROP_FPS) or 30

writer = cv2.VideoWriter('saida_anotada.mp4',
                         cv2.VideoWriter_fourcc(*'mp4v'),
                         fps, (w, h))

print(f'Processando {total} frames... aguarde.')
n = 0
ultimas_preds = []

while True:
    ok, frame = cap.read()
    if not ok:
        break
    n += 1
    if n % PROCESSAR_A_CADA == 0:
        ultimas_preds = detectar_frame(frame)
    frame = desenhar(frame, ultimas_preds)
    writer.write(frame)
    if n % 30 == 0:
        print(f'  {n}/{total} frames processados...')

cap.release()
writer.release()
print('Pronto! Vídeo salvo como saida_anotada.mp4')

# PASSO 4 — Baixar o vídeo anotado
from google.colab import files
files.download('saida_anotada.mp4')
