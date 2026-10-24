"""
Cadastra um usuário do sistema.

A senha nunca é gravada como texto, o werkzeug gera um hash com sal, e só
o hash vai para o banco. Nem o Admin consegue ver a senha de alguém.

Tem dois jeitos de cadastrar. O criar() não confere permissão e é usado
pelo criar_primeiro_usuario.py, no terminal, quando ainda não existe
ninguém logado. O executar() é o da API e só deixa o Admin cadastrar.
"""

from datetime import datetime

from werkzeug.security import generate_password_hash

from extensions import db
from models.usuario import Perfil, Usuario


class CriarUsuarioService:

    @staticmethod
    def criar(dados):
        """Cadastra o usuário SEM checar permissão.

        Uso interno, fora da API. É assim que o primeiro Administrador do
        sistema nasce, pelo script de terminal. Não ha usuário logado para
        conferir, e quem roda o script já tem acesso ao banco.
        """
        nome = (dados.get("nome") or "").strip()
        email = (dados.get("email") or "").strip().lower()
        senha = dados.get("senha") or ""

        if not nome:
            raise ValueError("O nome do usuário é obrigatório.")

        if not email or "@" not in email:
            raise ValueError("Informe um e-mail válido.")

        if len(senha) < 6:
            raise ValueError("A senha precisa ter ao menos 6 caracteres.")

        if Usuario.buscar_por_email(email):
            raise ValueError("Já existe um usuário com este e-mail.")

        perfil = db.session.get(Perfil, dados.get("perfil_id"))
        if not perfil:
            raise ValueError("Perfil inválido.")

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            perfil_id=perfil.id,
            ativo=True,
            criado_em=datetime.now(),
        )

        return usuario.salvar()

    @staticmethod
    def executar(dados, usuario_logado):
        if not usuario_logado.perfil or not usuario_logado.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario_logado.perfil.nome if usuario_logado.perfil else 'atual'} "
                "não tem permissão para cadastrar usuários. "
                "Somente o Administrador pode."
            )

        return CriarUsuarioService.criar(dados)
