"""
VetVision – Monitoramento Veterinário com IA
Módulo: Métricas do Modelo

Instalação:
    pip install roboflow opencv-python requests pyyaml

Uso:
    python rafa_metricas.py
"""

import os
import base64
import requests
import json
import yaml
import cv2
from pathlib import Path
from roboflow import Roboflow

# ──────────────────────────────────────────────
# Configurações
# ──────────────────────────────────────────────

ROBOFLOW_API_KEY = "NNRaoXh6QTL5y7mXASsa"
ROBOFLOW_MODEL   = "pi-liqod/3"
ROBOFLOW_URL     = f"https://serverless.roboflow.com/{ROBOFLOW_MODEL}"
CONFIANCA_MINIMA = 0.40
IOU_THRESHOLD    = 0.50

CLASSES = {0: "bowl", 1: "cat", 2: "dog"}

# ──────────────────────────────────────────────
# Passo 1 — Baixar dataset de teste
# ──────────────────────────────────────────────

print("[1/4] Baixando dataset do Roboflow...")
rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace("julias-workspace-phzrr").project("pi-liqod")
version = project.version(3)
dataset = version.download("yolov8-obb")

TEST_IMG_DIR = Path(dataset.location) / "test" / "images"
TEST_LBL_DIR = Path(dataset.location) / "test" / "labels"
print(f"Dataset salvo em: {dataset.location}")

# ──────────────────────────────────────────────
# Funções auxiliares
# ──────────────────────────────────────────────

def detectar(imagem_path):
    with open(imagem_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    try:
        resp = requests.post(
            ROBOFLOW_URL,
            params={"api_key": ROBOFLOW_API_KEY},
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        return resp.json().get("predictions", [])
    except Exception as e:
        print(f"[ERRO] {imagem_path.name}: {e}")
        return []

def ler_anotacoes_obb(label_path, img_w, img_h):
    boxes = []
    if not label_path.exists():
        return boxes
    with open(label_path) as f:
        for linha in f:
            partes = linha.strip().split()
            if len(partes) < 9:
                continue
            cls = int(partes[0])
            xs  = [float(partes[i]) * img_w for i in [1, 3, 5, 7]]
            ys  = [float(partes[i]) * img_h for i in [2, 4, 6, 8]]
            boxes.append({
                "classe": CLASSES.get(cls, str(cls)),
                "bbox": (min(xs), min(ys), max(xs), max(ys))
            })
    return boxes

def calcular_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter = max(0, xB - xA) * max(0, yB - yA)
    areaA = (boxA[2]-boxA[0]) * (boxA[3]-boxA[1])
    areaB = (boxB[2]-boxB[0]) * (boxB[3]-boxB[1])
    uniao = areaA + areaB - inter
    return inter / uniao if uniao > 0 else 0

# ──────────────────────────────────────────────
# Passo 2 — Rodar o modelo e comparar
# ──────────────────────────────────────────────

print("\n[2/4] Rodando modelo nas imagens de teste...")

TP = FP = FN = 0
imagens = list(TEST_IMG_DIR.glob("*.jpg")) + list(TEST_IMG_DIR.glob("*.png"))
print(f"Total de imagens de teste: {len(imagens)}")

for i, img_path in enumerate(imagens):
    img = cv2.imread(str(img_path))
    if img is None:
        continue
    img_h, img_w = img.shape[:2]

    lbl_path = TEST_LBL_DIR / (img_path.stem + ".txt")
    gabarito  = ler_anotacoes_obb(lbl_path, img_w, img_h)

    preds = detectar(img_path)
    deteccoes = []
    for p in preds:
        if float(p.get("confidence", 0)) < CONFIANCA_MINIMA:
            continue
        cx, cy, w, h = p["x"], p["y"], p["width"], p["height"]
        deteccoes.append({
            "classe": p.get("class", ""),
            "bbox": (cx-w/2, cy-h/2, cx+w/2, cy+h/2)
        })

    matched = set()
    for det in deteccoes:
        acertou = False
        for j, gt in enumerate(gabarito):
            if j in matched:
                continue
            if det["classe"] == gt["classe"]:
                if calcular_iou(det["bbox"], gt["bbox"]) >= IOU_THRESHOLD:
                    TP += 1
                    matched.add(j)
                    acertou = True
                    break
        if not acertou:
            FP += 1
    FN += len(gabarito) - len(matched)

    if (i+1) % 10 == 0:
        print(f"  {i+1}/{len(imagens)} imagens processadas...")

# ──────────────────────────────────────────────
# Passo 3 — Calcular métricas
# ──────────────────────────────────────────────

print("\n[3/4] Calculando métricas...")

precisao = TP / (TP + FP) if (TP + FP) > 0 else 0
recall   = TP / (TP + FN) if (TP + FN) > 0 else 0
f1       = 2 * precisao * recall / (precisao + recall) if (precisao + recall) > 0 else 0

print("\n" + "=" * 40)
print("📊 MÉTRICAS DO MODELO")
print("=" * 40)
print(f"  Verdadeiros Positivos (TP): {TP}")
print(f"  Falsos Positivos      (FP): {FP}")
print(f"  Falsos Negativos      (FN): {FN}")
print("─" * 40)
print(f"  Precisão:  {precisao:.2%}")
print(f"  Recall:    {recall:.2%}")
print(f"  F1 Score:  {f1:.2%}")
print("=" * 40)

# ──────────────────────────────────────────────
# Passo 4 — Salvar JSON pra integração
# ──────────────────────────────────────────────

metricas = {
    "TP": TP, "FP": FP, "FN": FN,
    "precisao": round(precisao, 4),
    "recall":   round(recall, 4),
    "f1":       round(f1, 4),
}

with open("metricas_modelo.json", "w") as f:
    json.dump(metricas, f, indent=2)

print("\n[4/4] Métricas salvas em metricas_modelo.json")
