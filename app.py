import json
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PASTA_RELATORIOS = Path("relatorios")
PASTA_EXEMPLOS   = Path("exemplos")
PASTA_UPLOADS    = Path("uploads")


@app.route("/relatorios", methods=["GET"])
def listar_relatorios():
    arquivos = sorted(
        PASTA_RELATORIOS.glob("relatorio_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    return jsonify([f.name for f in arquivos])


@app.route("/relatorios/<nome>", methods=["GET"])
def buscar_relatorio(nome):
    caminho = PASTA_RELATORIOS / nome
    if not caminho.exists():
        return jsonify({"erro": "Relatório não encontrado"}), 404
    with open(caminho, encoding="utf-8") as f:
        return jsonify(json.load(f))


@app.route("/video/<nome>", methods=["GET"])
def buscar_video(nome):
    for pasta in [PASTA_UPLOADS, Path("."), PASTA_EXEMPLOS]:
        caminho = pasta / nome
        if caminho.exists():
            return send_file(caminho, mimetype="video/mp4")
    return jsonify({"erro": "Vídeo não encontrado"}), 404


@app.route("/analisar", methods=["POST"])
def analisar():
    if "video" not in request.files:
        return jsonify({"erro": "Nenhum vídeo enviado"}), 400

    video = request.files["video"]
    PASTA_UPLOADS.mkdir(exist_ok=True)
    caminho_video = PASTA_UPLOADS / video.filename
    video.save(caminho_video)

    etapa1 = subprocess.run(
        ["python3", "detectar_objetos.py", str(caminho_video)],
        capture_output=True, text=True,
    )
    if etapa1.returncode != 0:
        return jsonify({"erro": etapa1.stderr}), 500

    etapa2 = subprocess.run(
        ["python3", "analisar_comportamento.py", str(caminho_video)],
        capture_output=True, text=True,
    )
    if etapa2.returncode != 0:
        return jsonify({"erro": etapa2.stderr}), 500

    relatorios = sorted(
        PASTA_RELATORIOS.glob("relatorio_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if not relatorios:
        return jsonify({"erro": "Relatório não gerado"}), 500

    with open(relatorios[0], encoding="utf-8") as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
