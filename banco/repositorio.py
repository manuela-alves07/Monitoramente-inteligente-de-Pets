from datetime import datetime

from banco.database import cursor_dict


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


def inserir_animal(nome, especie, raca, tutor, id_baia, status_internacao="internado"):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO animal (nome, especie, raca, tutor, id_baia, status_internacao)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_animal
            """,
            (nome, especie, raca, tutor, id_baia, status_internacao),
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
        cur.execute(
            "SELECT * FROM usuario WHERE email = %s AND senha_hash = %s",
            (login, senha),
        )
        return cur.fetchone()


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
            (nome, login, senha, role),
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
            (nova_senha, id_usuario),
        )


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
