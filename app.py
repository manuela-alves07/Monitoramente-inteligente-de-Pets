import json
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from banco.repositorio import (
    buscar_animal,
    dar_baixa,
    garantir_baias,
    inserir_animal,
    inserir_evento,
    inserir_alerta,
    listar_animais,
    listar_baias,
    listar_eventos,
)

app = Flask(__name__)
CORS(app)

PASTA_RELATORIOS = Path("relatorios")
PASTA_EXEMPLOS = Path("exemplos")
PASTA_UPLOADS = Path("uploads")


try:
    garantir_baias(6)
except Exception as exc:
    print(f"[aviso] banco indisponivel ao iniciar: {exc}")


def serializar(linha):
    if linha is None:
        return None
    saida = {}
    for chave, valor in linha.items():
        if hasattr(valor, "isoformat"):
            saida[chave] = valor.isoformat()
        else:
            saida[chave] = valor
    return saida


@app.route("/baias", methods=["GET"])
def rota_listar_baias():
    return jsonify([serializar(b) for b in listar_baias()])


@app.route("/animais", methods=["GET"])
def rota_listar_animais():
    return jsonify([serializar(a) for a in listar_animais()])


@app.route("/animais", methods=["POST"])
def rota_cadastrar_animal():
    dados = request.json or {}
    obrigatorios = ["nome", "especie", "id_baia", "tutor"]
    faltando = [c for c in obrigatorios if not dados.get(c)]
    if faltando:
        return jsonify({"erro": f"Campos obrigatorios: {', '.join(faltando)}"}), 400

    id_animal = inserir_animal(
        nome=dados["nome"],
        especie=dados["especie"],
        raca=dados.get("raca"),
        tutor=dados["tutor"],
        id_baia=int(dados["id_baia"]),
        status_internacao=dados.get("status_internacao", "internado"),
    )
    return jsonify(serializar(buscar_animal(id_animal))), 201


@app.route("/animais/<int:id_animal>", methods=["GET"])
def rota_buscar_animal(id_animal):
    animal = buscar_animal(id_animal)
    if not animal:
        return jsonify({"erro": "Animal nao encontrado"}), 404
    return jsonify(serializar(animal))


@app.route("/animais/<int:id_animal>/baixa", methods=["POST"])
def rota_dar_baixa(id_animal):
    if not buscar_animal(id_animal):
        return jsonify({"erro": "Animal nao encontrado"}), 404
    dar_baixa(id_animal)
    return jsonify({"ok": True})


@app.route("/animais/<int:id_animal>/eventos", methods=["GET"])
def rota_listar_eventos(id_animal):
    return jsonify([serializar(e) for e in listar_eventos(id_animal=id_animal)])


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
        relatorio = json.load(f)

    id_animal = request.form.get("id_animal")
    if id_animal:
        try:
            id_animal = int(id_animal)
            for ref in relatorio.get("refeicoes", []):
                inserir_evento(
                    id_animal=id_animal,
                    origem_camera=None,
                    tipo_evento="refeicao",
                    confianca_ia=ref.get("confianca"),
                )
            for alerta in relatorio.get("alertas", []):
                inserir_alerta(
                    id_animal=id_animal,
                    tipo_alerta=alerta.get("tipo", "info"),
                    descricao=alerta.get("mensagem", ""),
                )
        except Exception as exc:
            print(f"[aviso] falha ao gravar no banco: {exc}")

    return jsonify(relatorio)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
