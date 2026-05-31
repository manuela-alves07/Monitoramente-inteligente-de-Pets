import base64
import requests
import cv2
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta

VIDEO    = sys.argv[1] if len(sys.argv) > 1 else "exemplos/one_cat_eating.mp4"
SAIDA    = "comportamento_resultado.mp4"
MODO_API = len(sys.argv) > 1

ROBOFLOW_API_KEY = "NNRaoXh6QTL5y7mXASsa"
ROBOFLOW_MODEL   = "pi-liqod/3"
ROBOFLOW_URL     = f"https://serverless.roboflow.com/{ROBOFLOW_MODEL}"

CLASSES_PETS    = {'cat', 'dog'}
CLASSE_TIGELA   = 'bowl'
CONFIANCA_MIN   = 0.30

MAX_DIST_TRACKER   = 80
MAX_FRAMES_PERDIDO = 10

DIST_MAX          = 1.5
TEMPO_COMER_MIN   = 5
TEMPO_BEBER_MIN   = 3
TOLERANCIA_PAUSA  = 2
TEMPO_DESCANSO    = 5  * 60
TEMPO_AGITACAO    = 15 * 60
MOVIMENTO_BAIXO   = 1.5
MOVIMENTO_ALTO    = 15.0
PROCESSAR_A_CADA  = 5

ALERTA_SEM_COMER   = 6 * 3600
ALERTA_SEM_BEBER   = 4 * 3600
ALERTA_INATIVIDADE = 30 * 60

CORES_CLASSE = {'cat': (0, 200, 255), 'dog': (50, 220, 50)}


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
        print(f'[ERRO API] {e}')
        return []


def pred_para_bbox(pred):
    cx, cy = pred['x'], pred['y']
    w, h   = pred['width'], pred['height']
    return [int(cx - w/2), int(cy - h/2), int(cx + w/2), int(cy + h/2)]


def centro(bbox):
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)


def dist_px(c1, c2):
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2) ** 0.5


def dist_normalizada(animal_bbox, tigela_bbox):
    ax, ay = centro(animal_bbox)
    tx, ty = centro(tigela_bbox)
    dist   = ((ax - tx)**2 + (ay - ty)**2) ** 0.5
    largura = max(animal_bbox[2] - animal_bbox[0], 1)
    return dist / largura


def calc_movimento(hist):
    if len(hist) < 5:
        return 0
    dists = [((hist[i][0] - hist[i-1][0])**2 + (hist[i][1] - hist[i-1][1])**2) ** 0.5
             for i in range(1, len(hist))]
    return np.mean(dists)


def tipo_tigela(bbox, largura_frame):
    cx = (bbox[0] + bbox[2]) / 2
    return 'agua' if cx < largura_frame / 2 else 'comida'


def novo_animal():
    return {
        'hist':               [],
        'comendo_agora':      False,
        'inicio_refeicao':    None,
        'saiu_refeicao':      None,
        'bebendo_agora':      False,
        'inicio_bebida':      None,
        'saiu_bebida':        None,
        'ultima_refeicao':    None,
        'ultima_bebida':      None,
        'inicio_inatividade': None,
        'inicio_agitacao':    None,
        'estado':             'aguardando',
    }


tracks    = {}
proximo_id = 1

def atualizar_tracks(deteccoes_pets):
    global proximo_id

    for t in tracks.values():
        t['frames_perdidos'] += 1

    for det in deteccoes_pets:
        bbox   = pred_para_bbox(det)
        cx, cy = centro(bbox)
        classe = det['class']

        melhor_id   = None
        melhor_dist = MAX_DIST_TRACKER

        for tid, t in tracks.items():
            d = dist_px((cx, cy), (t['cx'], t['cy']))
            if d < melhor_dist:
                melhor_dist = d
                melhor_id   = tid

        if melhor_id is not None:
            tracks[melhor_id].update({'cx': cx, 'cy': cy, 'bbox': bbox,
                                      'classe': classe, 'frames_perdidos': 0})
        else:
            tracks[proximo_id] = {'cx': cx, 'cy': cy, 'bbox': bbox,
                                  'classe': classe, 'frames_perdidos': 0}
            proximo_id += 1

    ids_remover = [tid for tid, t in tracks.items()
                   if t['frames_perdidos'] > MAX_FRAMES_PERDIDO]
    for tid in ids_remover:
        del tracks[tid]

    return {tid: t for tid, t in tracks.items() if t['frames_perdidos'] == 0}


cap     = cv2.VideoCapture(VIDEO)
fps     = cap.get(cv2.CAP_PROP_FPS) or 30.0
largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
altura  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(SAIDA, cv2.VideoWriter_fourcc(*'mp4v'), fps, (largura, altura))

inicio_video = datetime.now()
frame_n      = 0
agora        = inicio_video

animais = {}
eventos = []
alertas = []

if not MODO_API:
    cv2.namedWindow('VetVision — Monitoramento', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('VetVision — Monitoramento', 800, 600)

print('Monitorando comportamento...')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_n += 1
    agora = inicio_video + timedelta(seconds=frame_n / fps)

    if frame_n % PROCESSAR_A_CADA != 0:
        out.write(frame)
        continue

    predicoes = detectar_frame(frame)
    predicoes = [p for p in predicoes if float(p.get('confidence', 0)) >= CONFIANCA_MIN]

    tigelas_comida = []
    tigelas_agua   = []

    for pred in predicoes:
        if pred['class'] != CLASSE_TIGELA:
            continue
        bbox = pred_para_bbox(pred)
        conf = float(pred['confidence'])
        tipo = tipo_tigela(bbox, largura)
        if tipo == 'agua':
            tigelas_agua.append(bbox)
            cor, label = (255, 100, 0), f'Agua {conf:.0%}'
        else:
            tigelas_comida.append(bbox)
            cor, label = (255, 165, 0), f'Comida {conf:.0%}'
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), cor, 2)
        cv2.putText(frame, label, (bbox[0], bbox[1] - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 1)

    pets_detectados = [p for p in predicoes if p['class'] in CLASSES_PETS]
    ativos = atualizar_tracks(pets_detectados)

    for track_id, t in ativos.items():
        bbox   = t['bbox']
        classe = t['classe']
        conf   = next((p['confidence'] for p in pets_detectados
                       if pred_para_bbox(p) == bbox), 0)

        if track_id not in animais:
            animais[track_id] = novo_animal()

        a = animais[track_id]
        cx, cy = centro(bbox)
        a['hist'].append((cx, cy))
        if len(a['hist']) > 30:
            a['hist'].pop(0)

        movimento    = calc_movimento(a['hist'])
        perto_comida = any(dist_normalizada(bbox, t2) < DIST_MAX for t2 in tigelas_comida)
        perto_agua   = any(dist_normalizada(bbox, t2) < DIST_MAX for t2 in tigelas_agua)

        if perto_comida:
            a['saiu_refeicao'] = None
            if not a['comendo_agora']:
                a['comendo_agora']   = True
                a['inicio_refeicao'] = a['inicio_refeicao'] or agora
        else:
            if a['comendo_agora']:
                if a['saiu_refeicao'] is None:
                    a['saiu_refeicao'] = agora
                if (agora - a['saiu_refeicao']).total_seconds() > TOLERANCIA_PAUSA:
                    duracao = (a['saiu_refeicao'] - a['inicio_refeicao']).total_seconds()
                    a['comendo_agora']   = False
                    a['inicio_refeicao'] = None
                    a['saiu_refeicao']   = None
                    if duracao >= TEMPO_COMER_MIN:
                        a['ultima_refeicao'] = agora
                        eventos.append({'tipo': 'refeicao', 'animal_id': track_id,
                                        'inicio': (agora - timedelta(seconds=duracao)).strftime('%H:%M:%S'),
                                        'duracao_s': round(duracao, 1)})
                        print(f'  Refeição (ID {track_id}): {duracao:.1f}s')
                    else:
                        eventos.append({'tipo': 'cheirando', 'animal_id': track_id,
                                        'inicio': (agora - timedelta(seconds=duracao)).strftime('%H:%M:%S'),
                                        'duracao_s': round(duracao, 1)})

        if perto_agua:
            a['saiu_bebida'] = None
            if not a['bebendo_agora']:
                a['bebendo_agora'] = True
                a['inicio_bebida'] = a['inicio_bebida'] or agora
        else:
            if a['bebendo_agora']:
                if a['saiu_bebida'] is None:
                    a['saiu_bebida'] = agora
                if (agora - a['saiu_bebida']).total_seconds() > TOLERANCIA_PAUSA:
                    duracao = (a['saiu_bebida'] - a['inicio_bebida']).total_seconds()
                    a['bebendo_agora'] = False
                    a['inicio_bebida'] = None
                    a['saiu_bebida']   = None
                    if duracao >= TEMPO_BEBER_MIN:
                        a['ultima_bebida'] = agora
                        eventos.append({'tipo': 'agua', 'animal_id': track_id,
                                        'inicio': (agora - timedelta(seconds=duracao)).strftime('%H:%M:%S'),
                                        'duracao_s': round(duracao, 1)})
                        print(f'  Bebendo (ID {track_id}): {duracao:.1f}s')

        if movimento < MOVIMENTO_BAIXO and not perto_comida and not perto_agua:
            if a['inicio_inatividade'] is None:
                a['inicio_inatividade'] = agora
            a['inicio_agitacao'] = None
            tempo_inativo = (agora - a['inicio_inatividade']).total_seconds()
            if tempo_inativo >= TEMPO_DESCANSO:
                a['estado'] = 'DESCANSANDO'
            else:
                a['estado'] = 'parado'
        else:
            if a['inicio_inatividade'] is not None:
                tempo_inativo = (agora - a['inicio_inatividade']).total_seconds()
                if tempo_inativo >= TEMPO_DESCANSO:
                    eventos.append({'tipo': 'descanso', 'animal_id': track_id,
                                    'inicio': a['inicio_inatividade'].strftime('%H:%M:%S'),
                                    'duracao_s': round(tempo_inativo, 1)})
            a['inicio_inatividade'] = None

        if movimento > MOVIMENTO_ALTO and not perto_comida and not perto_agua:
            if a['inicio_agitacao'] is None:
                a['inicio_agitacao'] = agora
            tempo_agitado = (agora - a['inicio_agitacao']).total_seconds()
            a['estado'] = 'AGITADO' if tempo_agitado >= TEMPO_AGITACAO else 'ativo'
        else:
            if a['inicio_agitacao'] is not None:
                tempo_agitado = (agora - a['inicio_agitacao']).total_seconds()
                if tempo_agitado >= TEMPO_AGITACAO:
                    eventos.append({'tipo': 'agitacao', 'animal_id': track_id,
                                    'inicio': a['inicio_agitacao'].strftime('%H:%M:%S'),
                                    'duracao_s': round(tempo_agitado, 1)})
            a['inicio_agitacao'] = None

        if a['comendo_agora']:
            estado, cor = 'COMENDO', (0, 200, 0)
        elif a['bebendo_agora']:
            estado, cor = 'BEBENDO', (255, 200, 0)
        elif a['estado'] == 'DESCANSANDO':
            estado, cor = a['estado'], (100, 100, 255)
        elif a['estado'] == 'AGITADO':
            estado, cor = 'AGITADO', (0, 0, 255)
        else:
            ref_comer = a['ultima_refeicao'] or inicio_video
            ref_beber = a['ultima_bebida']   or inicio_video
            apatico   = ((agora - ref_comer).total_seconds() > 2 * 3600 and
                         (agora - ref_beber).total_seconds() > 2 * 3600)
            estado, cor = ('APATICO', (0, 0, 200)) if apatico else ('aguardando', (180, 180, 180))

        a['estado'] = estado
        cor_classe  = CORES_CLASSE.get(classe, (200, 200, 200))
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), cor_classe, 2)
        cv2.putText(frame, f'{classe} #{track_id}  {estado}  {conf:.0%}',
                    (bbox[0], bbox[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, cor, 1)

    a          = next(iter(animais.values())) if animais else None
    status_txt = a['estado'] if a else 'aguardando'
    status_cor = (0, 200, 0)   if status_txt == 'COMENDO'                      else \
                 (255, 200, 0) if status_txt == 'BEBENDO'                      else \
                 (0, 0, 255)   if status_txt in ('AGITADO', 'APATICO')         else \
                 (100, 100, 255) if status_txt == 'DESCANSANDO'               else \
                 (180, 180, 180)
    cv2.rectangle(frame, (0, 0), (400, 40), (20, 20, 20), -1)
    cv2.putText(frame, status_txt, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_cor, 2)

    out.write(frame)
    if not MODO_API:
        cv2.imshow('VetVision — Monitoramento', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()

for track_id, a in animais.items():
    if a['comendo_agora'] and a['inicio_refeicao']:
        duracao = (agora - a['inicio_refeicao']).total_seconds()
        if duracao >= TEMPO_COMER_MIN:
            eventos.append({'tipo': 'refeicao', 'animal_id': track_id,
                            'inicio': a['inicio_refeicao'].strftime('%H:%M:%S'),
                            'duracao_s': round(duracao, 1)})
    if a['bebendo_agora'] and a['inicio_bebida']:
        duracao = (agora - a['inicio_bebida']).total_seconds()
        if duracao >= TEMPO_BEBER_MIN:
            eventos.append({'tipo': 'agua', 'animal_id': track_id,
                            'inicio': a['inicio_bebida'].strftime('%H:%M:%S'),
                            'duracao_s': round(duracao, 1)})
    if a['inicio_inatividade']:
        duracao = (agora - a['inicio_inatividade']).total_seconds()
        if duracao >= TEMPO_DESCANSO:
            eventos.append({'tipo': 'descanso', 'animal_id': track_id,
                            'inicio': a['inicio_inatividade'].strftime('%H:%M:%S'),
                            'duracao_s': round(duracao, 1)})

for track_id, a in animais.items():
    ref_comer = a['ultima_refeicao'] or inicio_video
    ref_beber = a['ultima_bebida']   or inicio_video
    sem_comer = (datetime.now() - ref_comer).total_seconds()
    sem_beber = (datetime.now() - ref_beber).total_seconds()
    if sem_comer > ALERTA_SEM_COMER:
        alertas.append({'tipo': 'sem_alimentacao', 'animal_id': track_id,
                        'mensagem': f'Animal está sem comer há {sem_comer/3600:.1f}h',
                        'nivel': 'critico'})
    if sem_beber > ALERTA_SEM_BEBER:
        alertas.append({'tipo': 'sem_hidratacao', 'animal_id': track_id,
                        'mensagem': f'Animal está sem beber há {sem_beber/3600:.1f}h',
                        'nivel': 'critico'})

if not any(e['tipo'] == 'refeicao' for e in eventos):
    alertas.append({'tipo': 'sem_refeicao_detectada',
                    'mensagem': 'Nenhuma refeição confirmada no período',
                    'nivel': 'aviso'})

out.release()
if not MODO_API:
    cv2.destroyAllWindows()

refeicoes = [e for e in eventos if e['tipo'] == 'refeicao']
bebidas   = [e for e in eventos if e['tipo'] == 'agua']
descansos = [e for e in eventos if e['tipo'] == 'descanso']
agitacoes = [e for e in eventos if e['tipo'] == 'agitacao']

print('\n=== RELATÓRIO ===')
print(f'Refeições  : {len(refeicoes)}')
print(f'Hidratações: {len(bebidas)}')
print(f'Descansos  : {len(descansos)}')
print(f'Agitações  : {len(agitacoes)}')
print(f'Alertas    : {len(alertas)}')

relatorio = {
    'gerado_em':       datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data':            datetime.now().strftime('%Y-%m-%d'),
    'horario_inicio':  inicio_video.strftime('%H:%M:%S'),
    'horario_fim':     datetime.now().strftime('%H:%M:%S'),
    'video_analisado': VIDEO,
    'refeicoes':       refeicoes,
    'hidratacoes':     bebidas,
    'descansos':       descansos,
    'agitacoes':       agitacoes,
    'alertas':         alertas,
}

os.makedirs('relatorios', exist_ok=True)
nome_arquivo = f"relatorios/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(nome_arquivo, 'w', encoding='utf-8') as f:
    json.dump(relatorio, f, ensure_ascii=False, indent=2)

print(f'\nVídeo    : {SAIDA}')
print(f'Relatório: {nome_arquivo}')
if not MODO_API:
    input('\nPressione Enter para fechar...')
