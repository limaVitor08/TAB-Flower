"""
Caso de uso: atualizar os dados de um usuário.

A senha Não passa por aqui: tem Service próprio, porque trocar senha e um
caso de uso diferente de corrigir um nome ou mudar de perfil.

Esta edicao e restrita ao Administrador por causa de um campo especifico:
perfil_id. A Model aceita perfil_id entre os campos editaveis (e deve
aceitar - trocar alguem de funcao no escritório e uma operação legitima),
mas quem decide QUEM pode fazer isso e regra de negocio, e regra de
negocio mora no Service. Sem esta checagem, qualquer pessoa faria um PUT
no próprio id mandando perfil_id = 1 e viraria Administrador sozinha.
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
