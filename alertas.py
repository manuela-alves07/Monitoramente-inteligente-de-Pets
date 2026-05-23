from datetime import datetime


LIMITE_SEM_ALIMENTACAO_H = 6
LIMITE_APROXIMACOES_SEM_COMER = 3


def alerta(tipo, mensagem, nivel="aviso", pet_id=None):
    item = {
        "tipo": tipo,
        "mensagem": mensagem,
        "nivel": nivel,
    }
    if pet_id is not None:
        item["pet_id"] = str(pet_id)
    return item


def alertas_do_pet(pet, agora=None):
    """Gera alertas de um pet com base no historico detectado."""
    agora = agora or datetime.now()
    pet_id = str(pet.get("pet_id", "sem_id"))
    refeicoes = pet.get("refeicoes") or []
    cheiradas = pet.get("cheiradas") or []
    ultima_refeicao = pet.get("ultima_refeicao")

    alertas = []

    if ultima_refeicao:
        sem_comer = (agora - ultima_refeicao).total_seconds()
        if sem_comer > LIMITE_SEM_ALIMENTACAO_H * 3600:
            alertas.append(
                alerta(
                    "sem_alimentacao",
                    f"Pet {pet_id} sem comer ha {sem_comer / 3600:.1f}h",
                    "critico",
                    pet_id,
                )
            )

    if not refeicoes:
        alertas.append(
            alerta(
                "sem_refeicao_detectada",
                f"Pet {pet_id} nao teve refeicao confirmada no periodo",
                "aviso",
                pet_id,
            )
        )

    if len(cheiradas) >= LIMITE_APROXIMACOES_SEM_COMER and not refeicoes:
        alertas.append(
            alerta(
                "muitas_aproximacoes",
                f"Pet {pet_id} se aproximou varias vezes sem confirmar alimentacao",
                "atencao",
                pet_id,
            )
        )

    return alertas


def alertas_gerais(pets, eventos, cheiradas=None, agora=None):
    """Gera alertas que consideram o video inteiro."""
    agora = agora or datetime.now()
    cheiradas = cheiradas or []

    alertas = []

    if not eventos:
        alertas.append(
            alerta(
                "sem_refeicao_detectada",
                "Nenhuma refeicao confirmada no periodo",
                "aviso",
            )
        )
        if len(cheiradas) >= LIMITE_APROXIMACOES_SEM_COMER:
            alertas.append(
                alerta(
                    "muitas_aproximacoes",
                    "O pet se aproximou varias vezes da tigela, mas nao teve refeicao confirmada",
                    "atencao",
                )
            )
        return alertas

    ultimas = [pet.get("ultima_refeicao") for pet in pets.values() if pet.get("ultima_refeicao")]
    if ultimas:
        ultima_refeicao = max(ultimas)
        sem_comer = (agora - ultima_refeicao).total_seconds()
        if sem_comer > LIMITE_SEM_ALIMENTACAO_H * 3600:
            alertas.append(
                alerta(
                    "sem_alimentacao",
                    f"Nenhum pet come ha {sem_comer / 3600:.1f}h",
                    "critico",
                )
            )

    return alertas


def aplicar_alertas(relatorio, pets, eventos, agora=None):
    """Preenche os alertas do relatorio e de cada pet."""
    agora = agora or datetime.now()
    cheiradas = relatorio.get("cheiradas") or []
    relatorio["alertas"] = []
    relatorio["pets"] = {}

    for pet in pets.values():
        pet_alertas = alertas_do_pet(pet, agora)
        pet["alertas"] = pet_alertas
        relatorio["alertas"].extend(pet_alertas)
        relatorio["pets"][str(pet["pet_id"])] = {
            "pet_id": str(pet["pet_id"]),
            "tipo": pet["tipo"],
            "refeicoes": pet["refeicoes"],
            "cheiradas": pet["cheiradas"],
            "alertas": pet_alertas,
        }

    relatorio["alertas"].extend(alertas_gerais(pets, eventos, cheiradas, agora))
    return relatorio
