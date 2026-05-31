import json
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from banco.repositorio import (
    autenticar_usuario,
    atualizar_animal,
    atualizar_senha_usuario,
    buscar_animal,
    buscar_relatorio_animal,
    criar_baia,
    dar_baixa,
    garantir_baias,
    garantir_tabela_relatorio,
    inserir_animal,
    inserir_evento,
    inserir_alerta,
    inserir_relatorio,
    inserir_usuario,
    listar_animais,
    listar_baias,
    listar_eventos,
    listar_relatorios_animal,
    listar_usuarios,
    migrar_senhas_em_texto,
    padronizar_tipos_evento,
    remover_baia,
    remover_usuario,
)

app = Flask(__name__)
CORS(app)

PASTA_EXEMPLOS = Path("exemplos")
PASTA_UPLOADS = Path("uploads")


try:
    garantir_baias(6)
    garantir_tabela_relatorio()
    convertidas = migrar_senhas_em_texto()
    if convertidas:
        print(f"[migracao] {convertidas} senha(s) em texto convertidas para hash")
    ajustados = padronizar_tipos_evento()
    if ajustados:
        print(f"[migracao] {ajustados} evento(s) 'comendo' renomeados para 'refeicao'")
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


@app.route("/baias", methods=["POST"])
def rota_criar_baia():
    baia = criar_baia()
    return jsonify(serializar(baia)), 201


@app.route("/baias/<int:id_baia>", methods=["DELETE"])
def rota_remover_baia(id_baia):
    remover_baia(id_baia)
    return jsonify({"ok": True})


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
        tutor=dados["tutor"],
        id_baia=int(dados["id_baia"]),
        raca=dados.get("raca"),
        idade=dados.get("idade"),
        peso=dados.get("peso"),
        telefone=dados.get("telefone"),
        motivo=dados.get("motivo"),
        diagnostico=dados.get("diagnostico"),
        medicamentos=dados.get("medicamentos"),
        alergias=dados.get("alergias"),
        veterinario=dados.get("veterinario"),
    )
    return jsonify(serializar(buscar_animal(id_animal))), 201


@app.route("/animais/<int:id_animal>", methods=["GET"])
def rota_buscar_animal(id_animal):
    animal = buscar_animal(id_animal)
    if not animal:
        return jsonify({"erro": "Animal nao encontrado"}), 404
    return jsonify(serializar(animal))


@app.route("/animais/<int:id_animal>", methods=["PUT"])
def rota_atualizar_animal(id_animal):
    if not buscar_animal(id_animal):
        return jsonify({"erro": "Animal nao encontrado"}), 404
    dados = request.json or {}
    atualizar_animal(
        id_animal,
        nome=dados.get("nome"),
        especie=dados.get("especie"),
        raca=dados.get("raca"),
        tutor=dados.get("tutor"),
        telefone=dados.get("telefone"),
        idade=dados.get("idade"),
        peso=dados.get("peso"),
        motivo=dados.get("motivo"),
        diagnostico=dados.get("diagnostico"),
        medicamentos=dados.get("medicamentos"),
        alergias=dados.get("alergias"),
        veterinario=dados.get("veterinario"),
    )
    return jsonify(serializar(buscar_animal(id_animal)))


@app.route("/animais/<int:id_animal>/baixa", methods=["POST"])
def rota_dar_baixa(id_animal):
    if not buscar_animal(id_animal):
        return jsonify({"erro": "Animal nao encontrado"}), 404
    dados = request.get_json(silent=True) or {}
    dar_baixa(
        id_animal,
        condicao_alta=dados.get("condicao_alta"),
        diagnostico_final=dados.get("diagnostico_final"),
        medicamentos_alta=dados.get("medicamentos_alta"),
        instrucoes_alta=dados.get("instrucoes_alta"),
        data_retorno=dados.get("data_retorno") or None,
    )
    return jsonify({"ok": True})


@app.route("/animais/<int:id_animal>/eventos", methods=["GET"])
def rota_listar_eventos(id_animal):
    return jsonify([serializar(e) for e in listar_eventos(id_animal=id_animal)])


@app.route("/usuarios/login", methods=["POST"])
def rota_login():
    dados = request.json or {}
    user = autenticar_usuario(dados.get("login", "").strip(), dados.get("senha", ""))
    if not user:
        return jsonify({"erro": "Usuário ou senha incorretos"}), 401
    return jsonify(serializar(user))


@app.route("/usuarios", methods=["GET"])
def rota_listar_usuarios():
    return jsonify([serializar(u) for u in listar_usuarios()])


@app.route("/usuarios", methods=["POST"])
def rota_inserir_usuario():
    dados = request.json or {}
    if not dados.get("nome") or not dados.get("login") or not dados.get("senha"):
        return jsonify({"erro": "Nome, login e senha são obrigatórios"}), 400
    try:
        id_usuario = inserir_usuario(
            nome=dados["nome"].strip(),
            login=dados["login"].strip(),
            senha=dados["senha"],
            role=dados.get("role", "user"),
        )
        return jsonify({"id_usuario": id_usuario}), 201
    except Exception:
        return jsonify({"erro": "Login já existe"}), 409


@app.route("/usuarios/<int:id_usuario>", methods=["DELETE"])
def rota_remover_usuario(id_usuario):
    remover_usuario(id_usuario)
    return jsonify({"ok": True})


@app.route("/usuarios/<int:id_usuario>/senha", methods=["PUT"])
def rota_atualizar_senha(id_usuario):
    dados = request.json or {}
    nova_senha = dados.get("senha", "").strip()
    if not nova_senha:
        return jsonify({"erro": "Senha não pode ser vazia"}), 400
    atualizar_senha_usuario(id_usuario, nova_senha)
    return jsonify({"ok": True})


@app.route("/animais/<int:id_animal>/relatorio", methods=["GET"])
def rota_buscar_relatorio_animal(id_animal):
    id_relatorio = request.args.get("id", type=int)
    data_filtro = request.args.get("data")
    dados = buscar_relatorio_animal(id_animal, data_filtro, id_relatorio)
    if not dados:
        return jsonify({"erro": "Relatório não encontrado"}), 404
    return jsonify(dados)


@app.route("/animais/<int:id_animal>/relatorios", methods=["GET"])
def rota_listar_relatorios_animal(id_animal):
    return jsonify(listar_relatorios_animal(id_animal))


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
        [sys.executable, "detectar_objetos.py", str(caminho_video)],
        capture_output=True, text=True,
    )
    if etapa1.returncode != 0:
        return jsonify({"erro": etapa1.stderr or etapa1.stdout or "Falha na detecao"}), 500

    etapa2 = subprocess.run(
        [sys.executable, "analisar_comportamento.py", str(caminho_video)],
        capture_output=True, text=True,
    )
    if etapa2.returncode != 0:
        return jsonify({"erro": etapa2.stderr or etapa2.stdout or "Falha na analise"}), 500

    marcador = "===RELATORIO_JSON==="
    if marcador not in etapa2.stdout:
        return jsonify({"erro": "Relatório não gerado pelo script de análise"}), 500
    linha_json = etapa2.stdout.split(marcador, 1)[1].strip().splitlines()[0]
    try:
        relatorio = json.loads(linha_json)
    except json.JSONDecodeError as exc:
        return jsonify({"erro": f"Saida do analisador invalida: {exc}"}), 500

    id_animal_raw = request.form.get("id_animal")
    if id_animal_raw:
        try:
            id_animal = int(id_animal_raw)
            relatorio["id_animal"] = id_animal

            inserir_relatorio(id_animal, relatorio)

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
    # use_reloader=False evita reinicio no meio da analise de video
    app.run(debug=True, port=5000, use_reloader=False)
