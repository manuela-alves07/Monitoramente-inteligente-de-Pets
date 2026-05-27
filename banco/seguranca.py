"""Hash de senha com scrypt (biblioteca padrao do Python, sem dependencia nova)."""
import hashlib
import hmac
import os
from base64 import b64decode, b64encode

N = 2 ** 14
R = 8
P = 1
DKLEN = 64
SALT_LEN = 16


def gerar_hash(senha):
    if not senha:
        raise ValueError("Senha vazia")
    salt = os.urandom(SALT_LEN)
    derivada = hashlib.scrypt(senha.encode("utf-8"), salt=salt, n=N, r=R, p=P, dklen=DKLEN)
    return "scrypt$" + b64encode(salt).decode() + "$" + b64encode(derivada).decode()


def verificar_senha(senha, hash_armazenado):
    if not hash_armazenado:
        return False
    try:
        algoritmo, salt_b64, derivada_b64 = hash_armazenado.split("$", 2)
    except ValueError:
        return False
    if algoritmo != "scrypt":
        return False
    try:
        salt = b64decode(salt_b64)
        esperado = b64decode(derivada_b64)
    except Exception:
        return False
    obtida = hashlib.scrypt(senha.encode("utf-8"), salt=salt, n=N, r=R, p=P, dklen=len(esperado))
    return hmac.compare_digest(obtida, esperado)
