import hashlib
import secrets


ITERACOES = 120_000


def gerar_hash(senha):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), ITERACOES).hex()
    return f"{salt}${h}"


def conferir(senha, registro):
    if not registro or "$" not in registro:
        return False
    salt, h = registro.split("$", 1)
    novo = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), ITERACOES).hex()
    return secrets.compare_digest(h, novo)


def parece_hash(valor):
    return isinstance(valor, str) and "$" in valor and len(valor) > 40
