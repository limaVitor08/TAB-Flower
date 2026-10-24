"""
Atualiza os dados de um usuário.

A senha não passa por aqui, ela tem um Service próprio. Só o Admin pode
editar usuários por causa do perfil_id. Sem essa trava, qualquer pessoa
mandaria um PUT no próprio cadastro com perfil_id = 1 e virava Admin.
"""

from extensions import db
from models.usuario import Perfil, Usuario


class AtualizarUsuarioService:
    @staticmethod
    def executar(id_usuario, dados, usuario_logado):
        if not usuario_logado.perfil or not usuario_logado.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario_logado.perfil.nome if usuario_logado.perfil else 'atual'} "
                "não tem permissão para editar usuários. "
                "Somente o Administrador pode."
            )

        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")

        if "nome" in dados and not (dados["nome"] or "").strip():
            raise ValueError("O nome do usuário é obrigatório.")

        if "email" in dados:
            email = (dados["email"] or "").strip().lower()
            if not email or "@" not in email:
                raise ValueError("Informe um e-mail válido.")

            # O e-mail identifica o usuário, entao não pode colidir.
            existente = Usuario.buscar_por_email(email)
            if existente and existente.id != usuario.id:
                raise ValueError("Já existe um usuário com este e-mail.")

            dados["email"] = email

        if "perfil_id" in dados:
            if not db.session.get(Perfil, dados["perfil_id"]):
                raise ValueError("Perfil inválido.")

        return usuario.atualizar(dados)
