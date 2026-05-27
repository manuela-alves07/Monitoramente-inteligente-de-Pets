from datetime import datetime

from banco.database import cursor_dict
from banco.seguranca import gerar_hash, verificar_senha


# --- Clinica ----------------------------------------------------------------

def inserir_clinica(nome, qtd_baias=6):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO clinica (nome, qtd_baias)
            VALUES (%s, %s)
            RETURNING id_clinica
            """,
            (nome, int(qtd_baias)),
        )
        id_clinica = cur.fetchone()["id_clinica"]
    garantir_baias(id_clinica, qtd_baias)
    return id_clinica


def buscar_clinica(id_clinica):
    with cursor_dict() as (_, cur):
        cur.execute(
            "SELECT id_clinica, nome, qtd_baias FROM clinica WHERE id_clinica = %s",
            (id_clinica,),
        )
        return cur.fetchone()


# --- Baias ------------------------------------------------------------------

def inserir_baia(numero, localizacao, id_clinica, status="livre"):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO baia (numero, localizacao, status, id_clinica)
            VALUES (%s, %s, %s, %s)
            RETURNING id_baia
            """,
            (numero, localizacao, status, id_clinica),
        )
        return cur.fetchone()["id_baia"]


def inserir_camera(id_baia, ip_stream, status="online"):
    with cursor_dict() as (_, cur):
        cur.execute(
            "INSERT INTO camera (id_baia, ip_stream, status) VALUES (%s, %s, %s) RETURNING id_camera",
            (id_baia, ip_stream, status),
        )
        return cur.fetchone()["id_camera"]


def garantir_baias(id_clinica, quantidade=6):
    with cursor_dict() as (_, cur):
        cur.execute(
            "SELECT COUNT(*) AS total FROM baia WHERE id_clinica = %s",
            (id_clinica,),
        )
        total = cur.fetchone()["total"]
        if total >= quantidade:
            return
        for n in range(total + 1, quantidade + 1):
            cur.execute(
                """
                INSERT INTO baia (numero, localizacao, status, id_clinica)
                VALUES (%s, %s, %s, %s)
                """,
                (f"B-{n:02d}", f"Sala {n}", "livre", id_clinica),
            )


def listar_baias(id_clinica):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT b.id_baia, b.numero, b.localizacao, b.status, b.id_clinica,
                   a.id_animal, a.nome, a.especie, a.raca, a.tutor,
                   a.status_internacao, a.data_entrada,
                   a.telefone, a.idade, a.peso, a.motivo,
                   a.diagnostico, a.medicamentos, a.alergias, a.veterinario
            FROM baia b
            LEFT JOIN animal a
                ON a.id_baia = b.id_baia AND a.status_internacao = 'internado'
            WHERE b.id_clinica = %s
            ORDER BY b.id_baia
            """,
            (id_clinica,),
        )
        return cur.fetchall()


def baia_da_clinica(id_baia, id_clinica):
    with cursor_dict() as (_, cur):
        cur.execute(
            "SELECT id_baia FROM baia WHERE id_baia = %s AND id_clinica = %s",
            (id_baia, id_clinica),
        )
        return cur.fetchone() is not None


# --- Animais ----------------------------------------------------------------

def inserir_animal(
    nome,
    especie,
    raca,
    tutor,
    id_baia,
    id_clinica,
    status_internacao="internado",
    telefone=None,
    idade=None,
    peso=None,
    motivo=None,
    diagnostico=None,
    medicamentos=None,
    alergias=None,
    veterinario=None,
):
    if not baia_da_clinica(id_baia, id_clinica):
        raise ValueError("Baia nao pertence a esta clinica")
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO animal (
                nome, especie, raca, tutor, id_baia, status_internacao,
                telefone, idade, peso, motivo, diagnostico,
                medicamentos, alergias, veterinario
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_animal
            """,
            (
                nome, especie, raca, tutor, id_baia, status_internacao,
                telefone, idade, peso, motivo, diagnostico,
                medicamentos, alergias, veterinario,
            ),
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


def listar_animais(id_clinica):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT a.id_animal, a.nome, a.especie, a.raca, a.tutor,
                   a.status_internacao, a.data_entrada, b.numero AS baia,
                   a.telefone, a.idade, a.peso, a.motivo,
                   a.diagnostico, a.medicamentos, a.alergias, a.veterinario
            FROM animal a
            JOIN baia b ON b.id_baia = a.id_baia
            WHERE b.id_clinica = %s
            ORDER BY a.data_entrada DESC
            """,
            (id_clinica,),
        )
        return cur.fetchall()


def buscar_animal(id_animal, id_clinica=None):
    with cursor_dict() as (_, cur):
        if id_clinica is not None:
            cur.execute(
                """
                SELECT a.*, b.numero AS baia, b.id_clinica
                FROM animal a
                JOIN baia b ON b.id_baia = a.id_baia
                WHERE a.id_animal = %s AND b.id_clinica = %s
                """,
                (id_animal, id_clinica),
            )
        else:
            cur.execute(
                """
                SELECT a.*, b.numero AS baia, b.id_clinica
                FROM animal a
                LEFT JOIN baia b ON b.id_baia = a.id_baia
                WHERE a.id_animal = %s
                """,
                (id_animal,),
            )
        return cur.fetchone()


def dar_baixa(id_animal, id_clinica):
    if not buscar_animal(id_animal, id_clinica):
        raise ValueError("Animal nao encontrado nesta clinica")
    with cursor_dict() as (_, cur):
        cur.execute(
            "UPDATE animal SET status_internacao = 'alta' WHERE id_animal = %s",
            (id_animal,),
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


# --- Usuarios ---------------------------------------------------------------

def inserir_usuario(nome, email, senha, id_clinica, perfil="operador"):
    senha_hash = gerar_hash(senha)
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            INSERT INTO usuario (nome, email, senha_hash, perfil, id_clinica)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_usuario
            """,
            (nome, email.lower(), senha_hash, perfil, id_clinica),
        )
        return cur.fetchone()["id_usuario"]


def buscar_usuario_por_email(email):
    with cursor_dict() as (_, cur):
        cur.execute(
            """
            SELECT u.id_usuario, u.nome, u.email, u.senha_hash, u.perfil, u.id_clinica,
                   c.nome AS nome_clinica, c.qtd_baias
            FROM usuario u
            JOIN clinica c ON c.id_clinica = u.id_clinica
            WHERE u.email = %s
            """,
            ((email or "").lower(),),
        )
        return cur.fetchone()


def autenticar(email, senha):
    usuario = buscar_usuario_por_email(email)
    if not usuario:
        return None
    if not verificar_senha(senha, usuario["senha_hash"]):
        return None
    return {
        "id_usuario": usuario["id_usuario"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "perfil": usuario["perfil"],
        "id_clinica": usuario["id_clinica"],
        "nome_clinica": usuario["nome_clinica"],
        "qtd_baias": usuario["qtd_baias"],
    }
