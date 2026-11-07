# Edita os dados de um usuário, só o Admin pode
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

        if "ativo" in dados and not dados["ativo"]:
            raise ValueError("Para desativar o usuário, use o botão Desativar.")

        if "nome" in dados and not (dados["nome"] or "").strip():
            raise ValueError("O nome do usuário é obrigatório.")

        if "email" in dados:
            email = (dados["email"] or "").strip().lower()
            if not email or "@" not in email:
                raise ValueError("Informe um e-mail válido.")

            existente = Usuario.buscar_por_email(email)
            if existente and existente.id != usuario.id:
                raise ValueError("Já existe um usuário com este e-mail.")

            dados["email"] = email

        if "perfil_id" in dados:
            perfil = db.session.get(Perfil, dados["perfil_id"])
            if not perfil:
                raise ValueError("Perfil inválido.")

            if usuario.id == usuario_logado.id and not perfil.pode_excluir:
                raise ValueError(
                    "Você não pode tirar o perfil de Administrador da própria conta."
                )

        return usuario.atualizar(dados)
