import cv2
import base64
import requests
from pathlib import Path

ROBOFLOW_API_KEY  = 'NNRaoXh6QTL5y7mXASsa'
ROBOFLOW_MODEL    = 'pi-liqod/1'
ROBOFLOW_URL      = f'https://serverless.roboflow.com/{ROBOFLOW_MODEL}'

CLASSES_ALVO      = {'dog', 'cat', 'bowl'}
CONFIANCA_MINIMA  = 0.40
PROCESSAR_A_CADA  = 5

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


def desenhar_deteccoes(frame, predicoes):
    for pred in predicoes:
        classe = pred.get('class', '')
        if classe not in CLASSES_ALVO:
            continue
        confianca = float(pred.get('confidence', 0))
        if confianca < CONFIANCA_MINIMA:
            continue
        cx, cy = pred['x'], pred['y']
        w,  h  = pred['width'], pred['height']
        x1, y1 = int(cx - w / 2), int(cy - h / 2)
        x2, y2 = int(cx + w / 2), int(cy + h / 2)
        cor    = CORES.get(classe, (200, 200, 200))
        rotulo = f'{classe} {confianca:.0%}'
        cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
        (lw, lh), _ = cv2.getTextSize(rotulo, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - lh - 8), (x1 + lw + 4, y1), cor, -1)
        cv2.putText(frame, rotulo, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def processar_video(caminho_entrada, caminho_saida):
    caminho_entrada = Path(caminho_entrada)
    caminho_saida   = Path(caminho_saida)

    cap   = cv2.VideoCapture(str(caminho_entrada))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30

    writer = cv2.VideoWriter(
        str(caminho_saida),
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps, (w, h),
    )

    print(f'Detectando objetos em {total} frames...')
    n = 0
    ultimas_predicoes = []

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        if n % PROCESSAR_A_CADA == 0:
            ultimas_predicoes = detectar_frame(frame)
        frame = desenhar_deteccoes(frame, ultimas_predicoes)
        writer.write(frame)
        if n % 30 == 0:
            print(f'  {n}/{total} frames processados...')

    cap.release()
    writer.release()
    print(f'Vídeo anotado salvo em: {caminho_saida}')
    return str(caminho_saida)
