"""
Troca a senha de um usuário.

Tem dois caminhos. O definir_senha() troca sem conferir quem pediu e é
usado pelo criar_primeiro_usuario.py, no terminal. O executar() é o da
API, cada um troca a própria senha, e só o Admin troca a de outra
pessoa. Sem essa regra, qualquer um trocaria a senha do Admin e entraria
com a conta dele.
"""

from werkzeug.security import generate_password_hash

from extensions import db
from models.usuario import Usuario


class AlterarSenhaService:

    @staticmethod
    def definir_senha(id_usuario, senha_nova):
        """Troca a senha SEM checar permissão.
        """
        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")

        senha_nova = senha_nova or ""

        if len(senha_nova) < 6:
            raise ValueError("A senha precisa ter ao menos 6 caracteres.")

        usuario.senha_hash = generate_password_hash(senha_nova)
        db.session.commit()

        return usuario

    @staticmethod
    def executar(id_usuario, senha_nova, usuario_logado):
        """Troca a senha a pedido de alguem logado na API.

        Qualquer pessoa pode trocar a PRÓPRIA senha. Trocar a senha de
        outra pessoa e privilegio administrativo. Sem essa regra, uma
        Secretária trocaria a senha do Administrador, entraria com ela e
        teria acesso total, tornando inutil toda a Funcionalidade 20.
        """
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

        return AlterarSenhaService.definir_senha(id_usuario, senha_nova)
