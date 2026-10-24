"""
Cria o primeiro usuário do sistema, ou troca a senha de um que já existe.

Como o sistema exige login, a tela de cadastro de usuários só abre para
quem já entrou. Mas ninguém entra sem ter um usuário.

Rode uma vez, com o WAMP ligado, de dentro da pasta backend:

    python criar_primeiro_usuario.py

A senha passa pelo mesmo CriarUsuarioService da tela, então é gravada
com hash.
"""

from getpass import getpass

from app import create_app
from extensions import db
from models.usuario import Perfil, Usuario
from services.usuario.alterar_senha_service import AlterarSenhaService
from services.usuario.criar_usuario_service import CriarUsuarioService


def escolher_perfil():
    """Mostra os perfis do banco e devolve o id escolhido."""
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
    """Pede a senha duas vezes para evitar erro de digitação.
    """
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

        # Caso o e-mail já exista (por exemplo, os advogados criados por
        # SQL com senha 'TEMPORARIO'), oferecemos redefinir a senha em
        # vez de falhar com "e-mail já cadastrado".
        if existente:
            print(f"\nJá existe um usuário com este e-mail: {existente.nome}")
            resposta = input("Deseja redefinir a senha dele? (s/n) ").strip().lower()

            if resposta != "s":
                print("Nada foi alterado.")
                return

            senha = pedir_senha()
            # definir_senha() e não executar(): executar() exige saber quem
            # esta pedindo a troca, e aqui não ha usuário logado. Este
            # script roda no terminal, antes de existir qualquer sessão.
            AlterarSenhaService.definir_senha(existente.id, senha)

            # Um usuário desativado não consegue logar, então reativamos.
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
            # criar() e não executar(): pela mesma razão do definir_senha
            # acima. executar() exige um usuário logado para conferir a
            # permissão, e no terminal não existe sessão nenhuma. E este
            # script que cria o primeiro Administrador, entao não haveria
            # como ele já estar logado.
            usuario = CriarUsuarioService.criar(
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
