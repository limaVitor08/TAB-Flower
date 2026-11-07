# Cria o primeiro usuário pelo terminal ou troca a senha de um que já existe
from getpass import getpass

from app import create_app
from extensions import db
from models.usuario import Perfil, Usuario
from services.usuario.gravar_usuario_service import GravarUsuarioService
from services.usuario.redefinir_senha_service import RedefinirSenhaService


def escolher_perfil():
    perfis = Perfil.listar_todos()

    print("\nPerfis disponíveis:")
    for perfil in perfis:
        marca = " (pode excluir registros)" if perfil.pode_excluir else ""
        print(f"  {perfil.id} - {perfil.nome}{marca}")

    while True:
        escolha = input("Número do perfil: ").strip()
        for perfil in perfis:
            if str(perfil.id) == escolha:
                return perfil.id
        print("Perfil inválido. Digite um dos números listados acima.")


def pedir_senha():
    while True:
        senha = getpass("Senha (mínimo 6 caracteres): ")
        confirmacao = getpass("Digite a senha de novo: ")

        if senha != confirmacao:
            print("As senhas não conferem. Tente de novo.\n")
            continue

        if len(senha) < 6:
            print("A senha precisa ter ao menos 6 caracteres.\n")
            continue

        return senha


def main():
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("TabFlower - cadastro do primeiro usuário")
        print("=" * 60)

        email = input("\nE-mail: ").strip().lower()
        existente = Usuario.buscar_por_email(email)

        if existente:
            print(f"\nJá existe um usuário com este e-mail: {existente.nome}")
            resposta = input("Deseja redefinir a senha dele? (s/n) ").strip().lower()

            if resposta != "s":
                print("Nada foi alterado.")
                return

            senha = pedir_senha()
            RedefinirSenhaService.executar(existente.id, senha)

            if not existente.ativo:
                existente.ativo = True
                db.session.commit()

            print(f"\nSenha de {existente.nome} redefinida com sucesso.")
            print("Já é possível entrar pela tela de login.")
            return

        nome = input("Nome completo: ").strip()
        perfil_id = escolher_perfil()
        senha = pedir_senha()

        try:
            usuario = GravarUsuarioService.executar(
                {
                    "nome": nome,
                    "email": email,
                    "senha": senha,
                    "perfil_id": perfil_id,
                }
            )
        except ValueError as erro:
            print(f"\nNão foi possível cadastrar: {erro}")
            return

        print(f"\nUsuário criado: {usuario.nome} ({usuario.perfil.nome})")
        print("Já é possível entrar pela tela de login.")


if __name__ == "__main__":
    main()
