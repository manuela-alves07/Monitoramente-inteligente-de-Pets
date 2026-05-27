import json
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from banco.repositorio import (
    autenticar,
    buscar_animal,
    dar_baixa,
    garantir_baias,
    inserir_alerta,
    inserir_animal,
    inserir_evento,
    listar_baias,
    listar_eventos,
)

app = Flask(__name__)
CORS(app)

PASTA_RELATORIOS = Path("relatorios")
PASTA_EXEMPLOS = Path("exemplos")
PASTA_UPLOADS = Path("uploads")

PYTHON = sys.executable or "python"


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


def id_clinica_da_requisicao():
    bruto = request.headers.get("X-Id-Clinica") or request.args.get("id_clinica")
    if not bruto:
        return None
    try:
        return int(bruto)
    except (TypeError, ValueError):
        return None


# ---------- Autenticacao --------------------------------------------------

@app.route("/login", methods=["POST"])
def rota_login():
    dados = request.json or {}
    email = (dados.get("email") or "").strip()
    senha = dados.get("senha") or ""
    if not email or not senha:
        return jsonify({"erro": "Informe e-mail e senha"}), 400
    usuario = autenticar(email, senha)
    if not usuario:
        return jsonify({"erro": "Usuario ou senha invalidos"}), 401
    garantir_baias(usuario["id_clinica"], usuario.get("qtd_baias") or 6)
    return jsonify({"ok": True, "usuario": usuario})


# ---------- Baias e animais (por clinica) ---------------------------------

@app.route("/baias", methods=["GET"])
def rota_listar_baias():
    id_clinica = id_clinica_da_requisicao()
    if not id_clinica:
        return jsonify({"erro": "Clinica nao informada"}), 400
    return jsonify([serializar(b) for b in listar_baias(id_clinica)])


@app.route("/animais", methods=["POST"])
def rota_cadastrar_animal():
    id_clinica = id_clinica_da_requisicao()
    if not id_clinica:
        return jsonify({"erro": "Clinica nao informada"}), 400

    dados = request.json or {}
    obrigatorios = ["nome", "especie", "id_baia", "tutor"]
    faltando = [c for c in obrigatorios if not dados.get(c)]
    if faltando:
        return jsonify({"erro": f"Campos obrigatorios: {', '.join(faltando)}"}), 400

    try:
        id_animal = inserir_animal(
            nome=dados["nome"],
            especie=dados["especie"],
            raca=dados.get("raca"),
            tutor=dados["tutor"],
            id_baia=int(dados["id_baia"]),
            id_clinica=id_clinica,
            status_internacao=dados.get("status_internacao", "internado"),
            telefone=dados.get("telefone"),
            idade=dados.get("idade"),
            peso=dados.get("peso"),
            motivo=dados.get("motivo"),
            diagnostico=dados.get("diagnostico"),
            medicamentos=dados.get("medicamentos"),
            alergias=dados.get("alergias"),
            veterinario=dados.get("veterinario"),
        )
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400

    return jsonify(serializar(buscar_animal(id_animal, id_clinica))), 201


@app.route("/animais/<int:id_animal>", methods=["GET"])
def rota_buscar_animal(id_animal):
    id_clinica = id_clinica_da_requisicao()
    if not id_clinica:
        return jsonify({"erro": "Clinica nao informada"}), 400
    animal = buscar_animal(id_animal, id_clinica)
    if not animal:
        return jsonify({"erro": "Animal nao encontrado"}), 404
    return jsonify(serializar(animal))


@app.route("/animais/<int:id_animal>/baixa", methods=["POST"])
def rota_dar_baixa(id_animal):
    id_clinica = id_clinica_da_requisicao()
    if not id_clinica:
        return jsonify({"erro": "Clinica nao informada"}), 400
    try:
        dar_baixa(id_animal, id_clinica)
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 404
    return jsonify({"ok": True})


@app.route("/animais/<int:id_animal>/eventos", methods=["GET"])
def rota_listar_eventos(id_animal):
    id_clinica = id_clinica_da_requisicao()
    if id_clinica and not buscar_animal(id_animal, id_clinica):
        return jsonify({"erro": "Animal nao encontrado"}), 404
    return jsonify([serializar(e) for e in listar_eventos(id_animal=id_animal)])


# ---------- Relatorios e video --------------------------------------------

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
        return jsonify({"erro": "Relatorio nao encontrado"}), 404
    with open(caminho, encoding="utf-8") as f:
        return jsonify(json.load(f))


@app.route("/video/<nome>", methods=["GET"])
def buscar_video(nome):
    for pasta in [PASTA_UPLOADS, Path("."), PASTA_EXEMPLOS]:
        caminho = pasta / nome
        if caminho.exists():
            return send_file(caminho, mimetype="video/mp4")
    return jsonify({"erro": "Video nao encontrado"}), 404


@app.route("/analisar", methods=["POST"])
def analisar():
    if "video" not in request.files:
        return jsonify({"erro": "Nenhum video enviado"}), 400

    video = request.files["video"]
    PASTA_UPLOADS.mkdir(exist_ok=True)
    caminho_video = PASTA_UPLOADS / video.filename
    video.save(caminho_video)

    etapa1 = subprocess.run(
        [PYTHON, "detectar_objetos.py", str(caminho_video)],
        capture_output=True, text=True,
    )
    if etapa1.returncode != 0:
        return jsonify({"erro": etapa1.stderr}), 500

    etapa2 = subprocess.run(
        [PYTHON, "analisar_comportamento.py", str(caminho_video)],
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
        return jsonify({"erro": "Relatorio nao gerado"}), 500

    with open(relatorios[0], encoding="utf-8") as f:
        relatorio = json.load(f)

    id_animal = request.form.get("id_animal")
    id_clinica = id_clinica_da_requisicao()
    if id_animal and id_clinica:
        try:
            id_animal = int(id_animal)
            if buscar_animal(id_animal, id_clinica):
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
