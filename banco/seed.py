from banco.database import testar_conexao
from banco.repositorio import (
    inserir_alerta,
    inserir_animal,
    inserir_baia,
    inserir_camera,
    inserir_evento,
    listar_animais,
)


def main():
    info = testar_conexao()
    print("ok:", info["current_database"])

    id_baia = inserir_baia("B-01", "Sala 1", "ocupada")
    id_cam = inserir_camera(id_baia, "rtsp://192.168.0.10/stream")
    id_pet = inserir_animal("Thor", "Cao", "Golden", "Ana Silva", id_baia)
    inserir_evento(id_pet, id_cam, "refeicao", 92.5)
    inserir_alerta(id_pet, "sem_alimentacao", "Sem comer ha 6h")

    print("cadastros feitos")
    for row in listar_animais():
        print(row["nome"], "- baia", row["baia"])


if __name__ == "__main__":
    main()
