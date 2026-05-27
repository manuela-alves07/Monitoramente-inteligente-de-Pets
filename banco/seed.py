from banco.database import testar_conexao
from banco.repositorio import (
    buscar_clinica,
    garantir_baias,
    inserir_alerta,
    inserir_animal,
    inserir_camera,
    inserir_clinica,
    inserir_evento,
    listar_animais,
    listar_baias,
)


def main():
    info = testar_conexao()
    print("ok:", info["current_database"])

    if not buscar_clinica(1):
        inserir_clinica("Clinica Padrao", 6)
        print("clinica padrao criada (6 baias)")
    else:
        garantir_baias(1, 6)
        print("clinica padrao: baias garantidas")

    if not listar_animais(1):
        baias = listar_baias(1)
        baia = next((b for b in baias if b["numero"] == "B-01"), baias[0] if baias else None)
        if baia:
            id_baia = baia["id_baia"]
            id_cam = inserir_camera(id_baia, "rtsp://192.168.0.10/stream")
            id_pet = inserir_animal(
                nome="Thor",
                especie="cachorro",
                raca="Golden",
                tutor="Ana Silva",
                id_baia=id_baia,
                id_clinica=1,
                veterinario="Dra. Ana",
                motivo="Observacao pos-cirurgia",
            )
            inserir_evento(id_pet, id_cam, "comendo", 92.5)
            inserir_alerta(id_pet, "sem_alimentacao", "Sem comer ha 6h")
            print("exemplo: Thor na clinica 1, baia B-01")

    print("\nanimais clinica 1:")
    for row in listar_animais(1):
        print(" -", row["nome"], "- baia", row["baia"])


if __name__ == "__main__":
    main()
