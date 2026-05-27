import os
from contextlib import contextmanager
from urllib.parse import urlparse, unquote

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
HOST = os.getenv("PG_HOST", "localhost")
PORTA = int(os.getenv("PG_PORT", "5432"))
BANCO = os.getenv("PG_DB", "monitoramento_pets")
USUARIO = os.getenv("PG_USER", "postgres")
SENHA = os.getenv("PG_PASSWORD", "")
SSLMODE = os.getenv("PG_SSLMODE", "").strip()


def _conectar_por_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("postgresql", "postgres"):
        raise ValueError("DATABASE_URL deve comecar com postgresql://")
    query = dict(p.split("=", 1) for p in parsed.query.split("&") if "=" in p)
    sslmode = query.get("sslmode") or SSLMODE or None
    kwargs = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "dbname": parsed.path.lstrip("/"),
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
    }
    if sslmode:
        kwargs["sslmode"] = sslmode
    return psycopg2.connect(**kwargs)


def conectar():
    if DATABASE_URL:
        return _conectar_por_url(DATABASE_URL)
    kwargs = {
        "host": HOST,
        "port": PORTA,
        "dbname": BANCO,
        "user": USUARIO,
        "password": SENHA,
    }
    if SSLMODE:
        kwargs["sslmode"] = SSLMODE
    return psycopg2.connect(**kwargs)


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
