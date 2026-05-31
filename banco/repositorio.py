import json
from datetime import datetime

from banco.database import cursor_dict
from banco import senhas


def inserir_baia(numero, localizacao, status="livre"):
    with cursor_dict() as (_, cur):
        cur.execute(
            "INSERT INTO baia (numero, localizacao, status) VALUES (%s, %s, %s) RETURNING id_baia",
            (numero, localizacao, status),
        )
        return cur.fetchone()["id_baia"]


def inserir_camera(id_baia, ip_stream, status="online"):
    with cursor_dict() as (_, cur):
        cur.execute(
            "INSERT INTO camera (id_baia, ip_stream, status) VALUES (%s, %s, %s) RETURNING id_camera",
            (id_baia, ip_stream, status),
        )
        return cur.fetchone()["id_camera"]


def inserir_animal(nome, especie, tutor, id_baia, raca=None, idade=None, peso=None,
                   telefone=None, motivo=None, diagnostico=None, medicamentos=None,
                   alergias=None, veterinario=None, status_internacao="internado"):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO animal (nome, especie, raca, tutor, id_baia, status_internacao,
                                idade, peso, telefone, motivo, diagnostico,
                                medicamentos, alergias, veterinario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_animal
            """,
            (nome, especie, raca, tutor, id_baia, status_internacao,
             idade, peso, telefone, motivo, diagnostico, medicamentos, alergias, veterinario),
        )
        return cur.fetchone()["id_animal"]


def inserir_evento(id_animal, origem_camera, tipo_evento, confianca_ia=None, quando=None):
    quando = quando or datetime.now()
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO evento (id_animal, origem_camera, tipo_evento, confianca_ia, data_hora)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_evento
            """,
            (id_animal, origem_camera, tipo_evento, confianca_ia, quando),
        )
        return cur.fetchone()["id_evento"]


def inserir_alerta(id_animal, tipo_alerta, descricao, status="aberto"):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO alerta (id_animal, tipo_alerta, descricao, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id_alerta
            """,
            (id_animal, tipo_alerta, descricao, status),
        )
        return cur.fetchone()["id_alerta"]


def listar_animais():
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT a.id_animal, a.nome, a.especie, a.raca, a.tutor,
                   a.status_internacao, a.data_entrada, b.numero AS baia
            FROM animal a
            LEFT JOIN baia b ON b.id_baia = a.id_baia
            ORDER BY a.data_entrada DESC
            """
        )
        return cur.fetchall()


def listar_baias():
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT b.id_baia, b.numero, b.localizacao, b.status,
                   a.id_animal, a.nome, a.especie, a.raca, a.tutor,
                   a.status_internacao, a.data_entrada
            FROM baia b
            LEFT JOIN animal a
                ON a.id_baia = b.id_baia AND a.status_internacao = 'internado'
            ORDER BY b.numero
            """
        )
        return cur.fetchall()


def buscar_animal(id_animal):
    with cursor_dict() as (_, cur):
        cur.execute(
            "SELECT * FROM animal WHERE id_animal = %s",
            (id_animal,),
        )
        return cur.fetchone()


def atualizar_animal(id_animal, nome, especie, raca, tutor, telefone,
                     idade, peso, motivo, diagnostico, medicamentos, alergias, veterinario):
    with cursor_dict() as (_, cur):
        cur.execute(
            """UPDATE animal SET
                nome=%s, especie=%s, raca=%s, tutor=%s, telefone=%s,
                idade=%s, peso=%s, motivo=%s, diagnostico=%s,
                medicamentos=%s, alergias=%s, veterinario=%s
               WHERE id_animal=%s""",
            (nome, especie, raca, tutor, telefone,
             idade, peso, motivo, diagnostico, medicamentos, alergias, veterinario,
             id_animal),
        )


def dar_baixa(id_animal, condicao_alta=None, diagnostico_final=None,
              medicamentos_alta=None, instrucoes_alta=None, data_retorno=None):
    with cursor_dict() as (_, cur):
        cur.execute(
            """UPDATE animal SET
                status_internacao = 'alta',
                data_alta = NOW(),
                condicao_alta = %s,
                diagnostico_final = %s,
                medicamentos_alta = %s,
                instrucoes_alta = %s,
                data_retorno = %s
               WHERE id_animal = %s""",
            (condicao_alta, diagnostico_final, medicamentos_alta, instrucoes_alta, data_retorno, id_animal),
        )


def criar_baia():
    with cursor_dict() as (_, cur):
        cur.execute("SELECT COALESCE(MAX(id_baia), 0) + 1 AS proximo FROM baia")
        proximo = cur.fetchone()["proximo"]
        numero = f"B-{proximo:02d}"
        cur.execute(
            "INSERT INTO baia (numero, localizacao, status) VALUES (%s, %s, 'livre') RETURNING id_baia, numero, localizacao, status",
            (numero, f"Sala {proximo}"),
        )
        return cur.fetchone()


def remover_baia(id_baia):
    with cursor_dict() as (_, cur):
        cur.execute(
            """DELETE FROM baia WHERE id_baia = %s
               AND NOT EXISTS (
                 SELECT 1 FROM animal WHERE id_baia = %s AND status_internacao = 'internado'
               )""",
            (id_baia, id_baia),
        )


def garantir_baias(quantidade=6):
    with cursor_dict() as (_, cur):
        cur.execute("SELECT COUNT(*) AS total FROM baia")
        total = cur.fetchone()["total"]
        if total >= quantidade:
            return
        for n in range(total + 1, quantidade + 1):
            cur.execute(
                "INSERT INTO baia (numero, localizacao, status) VALUES (%s, %s, %s)",
                (f"B-{n:02d}", f"Sala {n}", "livre"),
            )


def listar_eventos(id_animal=None, limite=50):
    sql = """
        SELECT id_evento, id_animal, origem_camera, tipo_evento,
               confianca_ia, data_hora
        FROM evento
    """
    params = []
    if id_animal is not None:
        sql += " WHERE id_animal = %s"
        params.append(id_animal)
    sql += " ORDER BY data_hora DESC LIMIT %s"
    params.append(limite)

    with cursor_dict() as (_, cur):
        cur.execute(sql, params)
        return cur.fetchall()


def autenticar_usuario(login, senha):
    with cursor_dict() as (_, cur):
        cur.execute("SELECT * FROM usuario WHERE email = %s", (login,))
        user = cur.fetchone()
    if not user:
        return None
    armazenada = user.get("senha_hash") or ""
    if senhas.parece_hash(armazenada):
        return user if senhas.conferir(senha, armazenada) else None
    if armazenada == senha:
        atualizar_senha_usuario(user["id_usuario"], senha)
        return user
    return None


def listar_usuarios():
    with cursor_dict() as (_, cur):
        cur.execute(
            "SELECT id_usuario, nome, email AS login, perfil AS role FROM usuario ORDER BY id_usuario"
        )
        return cur.fetchall()


def inserir_usuario(nome, login, senha, role="user"):
    with cursor_dict() as (_, cur):
        cur.execute(
            """INSERT INTO usuario (nome, email, senha_hash, perfil, id_clinica)
               VALUES (%s, %s, %s, %s, 1) RETURNING id_usuario""",
            (nome, login, senhas.gerar_hash(senha), role),
        )
        return cur.fetchone()["id_usuario"]


def remover_usuario(id_usuario):
    with cursor_dict() as (_, cur):
        cur.execute(
            "DELETE FROM usuario WHERE id_usuario = %s AND email != 'admin'",
            (id_usuario,),
        )


def atualizar_senha_usuario(id_usuario, nova_senha):
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE usuario SET senha_hash = %s WHERE id_usuario = %s",
            (senhas.gerar_hash(nova_senha), id_usuario),
        )


def migrar_senhas_em_texto():
    with cursor_dict() as (_, cur):
        cur.execute("SELECT id_usuario, senha_hash FROM usuario")
        usuarios = cur.fetchall()
        convertidas = 0
        for u in usuarios:
            atual = u.get("senha_hash") or ""
            if senhas.parece_hash(atual):
                continue
            novo = senhas.gerar_hash(atual)
            cur.execute(
                "UPDATE usuario SET senha_hash = %s WHERE id_usuario = %s",
                (novo, u["id_usuario"]),
            )
            convertidas += 1
        return convertidas


def listar_alertas_abertos():
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT id_alerta, id_animal, tipo_alerta, descricao, status, criado_em
            FROM alerta
            WHERE status = 'aberto'
            ORDER BY criado_em DESC
            """
        )
        return cur.fetchall()


def padronizar_tipos_evento():
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE evento SET tipo_evento = 'refeicao' WHERE tipo_evento = 'comendo'"
        )
        return cur.rowcount


def garantir_tabela_relatorio():
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS relatorio_analise (
                id_relatorio SERIAL PRIMARY KEY,
                id_animal    INTEGER NOT NULL REFERENCES animal(id_animal) ON DELETE CASCADE,
                data         DATE NOT NULL,
                gerado_em    TIMESTAMP NOT NULL DEFAULT NOW(),
                dados        JSONB NOT NULL
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_rel_animal_data ON relatorio_analise (id_animal, data DESC)"
        )


def inserir_relatorio(id_animal, dados):
    agora = datetime.now()
    data = dados.get("data") or agora.strftime("%Y-%m-%d")
    gerado_em = dados.get("gerado_em") or agora.strftime("%Y-%m-%d %H:%M:%S")
    with cursor_dict() as (_, cur):
        cur.execute(
            """INSERT INTO relatorio_analise (id_animal, data, gerado_em, dados)
               VALUES (%s, %s, %s, %s::jsonb) RETURNING id_relatorio, gerado_em""",
            (id_animal, data, gerado_em, json.dumps(dados, ensure_ascii=False)),
        )
        return cur.fetchone()


def buscar_relatorio_animal(id_animal, data=None, id_relatorio=None):
    if id_relatorio:
        sql = "SELECT dados FROM relatorio_analise WHERE id_animal = %s AND id_relatorio = %s"
        params = [id_animal, id_relatorio]
    else:
        sql = "SELECT dados FROM relatorio_analise WHERE id_animal = %s"
        params = [id_animal]
        if data:
            sql += " AND data = %s"
            params.append(data)
        sql += " ORDER BY gerado_em DESC LIMIT 1"
    with cursor_dict() as (_, cur):
        cur.execute(sql, params)
        linha = cur.fetchone()
        return linha["dados"] if linha else None


def importar_relatorios_de_arquivos(pasta):
    from pathlib import Path
    pasta = Path(pasta)
    if not pasta.exists():
        return 0
    importados = 0
    with cursor_dict() as (_, cur):
        for arquivo in sorted(pasta.glob("relatorio_animal_*.json")):
            try:
                with open(arquivo, encoding="utf-8") as f:
                    dados = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            id_animal = dados.get("id_animal")
            gerado_em = dados.get("gerado_em")
            data = dados.get("data") or datetime.now().strftime("%Y-%m-%d")
            if not id_animal or not gerado_em:
                continue
            cur.execute(
                "SELECT 1 FROM relatorio_analise WHERE id_animal = %s AND gerado_em = %s",
                (id_animal, gerado_em),
            )
            if cur.fetchone():
                continue
            cur.execute(
                """INSERT INTO relatorio_analise (id_animal, data, gerado_em, dados)
                   VALUES (%s, %s, %s, %s::jsonb)""",
                (id_animal, data, gerado_em, json.dumps(dados, ensure_ascii=False)),
            )
            importados += 1
    return importados


def listar_relatorios_animal(id_animal):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT id_relatorio, data, gerado_em, dados
            FROM relatorio_analise
            WHERE id_animal = %s
            ORDER BY gerado_em DESC
            """,
            (id_animal,),
        )
        linhas = cur.fetchall()
    resumo = []
    for l in linhas:
        d = l["dados"] or {}
        resumo.append({
            "id_relatorio": l["id_relatorio"],
            "data": l["data"].isoformat() if hasattr(l["data"], "isoformat") else l["data"],
            "gerado_em": l["gerado_em"].strftime("%Y-%m-%d %H:%M:%S") if l["gerado_em"] else None,
            "refeicoes_confirmadas": d.get("refeicoes_confirmadas", 0),
            "total_alertas": len(d.get("alertas", [])),
        })
    return resumo
