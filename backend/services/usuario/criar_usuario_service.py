# Cadastra um usuário pela API, só o Admin pode
from services.usuario.gravar_usuario_service import GravarUsuarioService


class CriarUsuarioService:

    @staticmethod
    def executar(dados, usuario_logado):
        if not usuario_logado.perfil or not usuario_logado.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario_logado.perfil.nome if usuario_logado.perfil else 'atual'} "
                "não tem permissão para cadastrar usuários. "
                "Somente o Administrador pode."
            )

        return GravarUsuarioService.executar(dados)
