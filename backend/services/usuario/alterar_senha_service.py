# Troca a senha pela API, cada um a sua e o Admin a de qualquer um
from services.usuario.redefinir_senha_service import RedefinirSenhaService


class AlterarSenhaService:

    @staticmethod
    def executar(id_usuario, senha_nova, usuario_logado):
        e_a_propria = usuario_logado.id == id_usuario
        e_admin = bool(
            usuario_logado.perfil and usuario_logado.perfil.pode_excluir
        )

        if not e_a_propria and not e_admin:
            raise PermissionError(
                f"O perfil {usuario_logado.perfil.nome if usuario_logado.perfil else 'atual'} "
                "só pode alterar a própria senha. "
                "Somente o Administrador pode alterar a senha de outra pessoa."
            )

        return RedefinirSenhaService.executar(id_usuario, senha_nova)
