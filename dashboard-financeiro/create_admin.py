import getpass

from database import criar_tabelas, create_or_update_admin


def main():
    criar_tabelas()
    username = input("Usuario administrador: ").strip()
    password = getpass.getpass("Senha: ")

    if len(username) < 3:
        raise SystemExit("O usuario deve ter pelo menos 3 caracteres.")
    if len(password) < 8:
        raise SystemExit("A senha deve ter pelo menos 8 caracteres.")

    create_or_update_admin(username, password)
    print("Administrador criado ou atualizado com sucesso.")


if __name__ == "__main__":
    main()
