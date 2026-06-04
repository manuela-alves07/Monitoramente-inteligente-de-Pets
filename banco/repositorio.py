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


def inserir_evento(id_animal, origem_camera, tipo_evento, confianca_ia=None, quando=None, duracao_s=None):
    quando = quando or datetime.utcnow()
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO evento (id_animal, origem_camera, tipo_evento, confianca_ia, data_hora, duracao_s)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_evento
            """,
            (id_animal, origem_camera, tipo_evento, confianca_ia, quando, duracao_s),
        )
        return cur.fetchone()["id_evento"]


def inserir_alerta(id_animal, tipo_alerta, descricao, status="aberto"):
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE alerta SET status = 'fechado' WHERE id_animal = %s AND tipo_alerta = %s AND status = 'aberto'",
            (id_animal, tipo_alerta),
        )
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
                   a.status_internacao, a.data_entrada,
                   (SELECT e.data_hora FROM evento e
                    WHERE e.id_animal = a.id_animal AND e.tipo_evento = 'refeicao'
                    ORDER BY e.data_hora DESC LIMIT 1) AS ultima_refeicao,
                   (SELECT e.data_hora FROM evento e
                    WHERE e.id_animal = a.id_animal AND e.tipo_evento = 'agua'
                    ORDER BY e.data_hora DESC LIMIT 1) AS ultima_agua,
                   EXISTS (SELECT 1 FROM alerta al
                    WHERE al.id_animal = a.id_animal AND al.status = 'aberto') AS tem_alerta,
                   (SELECT al.descricao FROM alerta al
                    WHERE al.id_animal = a.id_animal AND al.status = 'aberto'
                    ORDER BY al.criado_em DESC LIMIT 1) AS descricao_alerta,
                   (SELECT al.id_alerta FROM alerta al
                    WHERE al.id_animal = a.id_animal AND al.status = 'aberto'
                    ORDER BY al.criado_em DESC LIMIT 1) AS id_alerta
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


def salvar_observacoes(id_animal, observacoes):
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE animal SET observacoes = %s WHERE id_animal = %s",
            (observacoes, id_animal),
        )


def transferir_baia(id_animal, id_baia_destino):
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE animal SET id_baia = %s WHERE id_animal = %s",
            (id_baia_destino, id_animal),
        )


def _upsert_alerta(id_animal, tipo_alerta, descricao):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO alerta (id_animal, tipo_alerta, descricao, status)
            VALUES (%s, %s, %s, 'aberto')
            ON CONFLICT (id_animal, tipo_alerta) WHERE status = 'aberto'
            DO UPDATE SET descricao = EXCLUDED.descricao
            """,
            (id_animal, tipo_alerta, descricao)
        )


def verificar_alertas_clinicos():
    LIMITE_COMER = 6 * 3600
    LIMITE_BEBER = 4 * 3600
    with cursor_dict() as (_, cur):
        cur.execute("""
            SELECT a.id_animal, a.nome,
                (SELECT e.data_hora FROM evento e
                 WHERE e.id_animal = a.id_animal AND e.tipo_evento = 'refeicao'
                 ORDER BY e.data_hora DESC LIMIT 1) AS ultima_refeicao,
                (SELECT e.data_hora FROM evento e
                 WHERE e.id_animal = a.id_animal AND e.tipo_evento = 'agua'
                 ORDER BY e.data_hora DESC LIMIT 1) AS ultima_agua
            FROM animal a
            WHERE a.status_internacao = 'internado'
        """)
        animais = cur.fetchall()

    agora = datetime.utcnow()
    for a in animais:
        sem_comer = (agora - a['ultima_refeicao']).total_seconds() if a['ultima_refeicao'] else None
        sem_beber = (agora - a['ultima_agua']).total_seconds() if a['ultima_agua'] else None

        if sem_comer is not None:
            if sem_comer > LIMITE_COMER:
                horas = int(round(sem_comer / 3600, 0))
                descricao = f"{a['nome']} está sem comer há mais de {horas} horas"
                _upsert_alerta(a['id_animal'], 'sem_alimentacao', descricao)
            else:
                fechar_alertas_tipo(a['id_animal'], 'sem_alimentacao')

        if sem_beber is not None:
            if sem_beber > LIMITE_BEBER:
                horas = int(round(sem_beber / 3600, 0))
                descricao = f"{a['nome']} está sem beber há mais de {horas} horas"
                _upsert_alerta(a['id_animal'], 'sem_hidratacao', descricao)
            else:
                fechar_alertas_tipo(a['id_animal'], 'sem_hidratacao')


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
               confianca_ia, data_hora, duracao_s
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


def garantir_admin():
    with cursor_dict() as (_, cur):
        cur.execute("SELECT id_usuario FROM usuario WHERE email = 'admin'")
        if not cur.fetchone():
            cur.execute(
                """INSERT INTO usuario (nome, email, senha_hash, perfil, id_clinica)
                   VALUES ('Administrador', 'admin', 'admin123', 'admin', 1)""",
            )


def autenticar_usuario(login, senha):
    with cursor_dict() as (_, cur):
        cur.execute(
            "SELECT *, perfil AS role, email AS login FROM usuario WHERE email = %s AND senha_hash = %s",
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


def listar_alertas_animal(id_animal):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT id_alerta, tipo_alerta, descricao, status, criado_em
            FROM alerta
            WHERE id_animal = %s
            ORDER BY criado_em DESC
            """,
            (id_animal,),
        )
        return cur.fetchall()


def fechar_alertas_tipo(id_animal, tipo_alerta):
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE alerta SET status = 'fechado' WHERE id_animal = %s AND tipo_alerta = %s AND status = 'aberto'",
            (id_animal, tipo_alerta),
        )


def fechar_alerta(id_alerta):
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE alerta SET status = 'fechado' WHERE id_alerta = %s",
            (id_alerta,),
        )


def listar_alertas_abertos():
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT al.id_alerta, al.id_animal, a.nome AS nome_animal,
                   al.tipo_alerta, al.descricao, al.status, al.criado_em
            FROM alerta al
            LEFT JOIN animal a ON a.id_animal = al.id_animal
            WHERE al.status = 'aberto'
            ORDER BY al.criado_em DESC
            """
        )
        return cur.fetchall()
