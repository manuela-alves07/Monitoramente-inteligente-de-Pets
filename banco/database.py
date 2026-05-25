import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("PG_HOST", "localhost")
PORTA = int(os.getenv("PG_PORT", "5432"))
BANCO = os.getenv("PG_DB", "monitoramento_pets")
USUARIO = os.getenv("PG_USER", "postgres")
SENHA = os.getenv("PG_PASSWORD", "")


def conectar():
    return psycopg2.connect(
        host=HOST,
        port=PORTA,
        dbname=BANCO,
        user=USUARIO,
        password=SENHA,
    )


@contextmanager
def cursor_dict():
    conn = conectar()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def testar_conexao():
    with cursor_dict() as (_, cur):
        cur.execute("SELECT current_database(), current_user, version();")
        return cur.fetchone()
