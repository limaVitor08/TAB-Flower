"""
Caso de uso: trocar a senha de um usuário.

Este Service tem DOIS caminhos de entrada, e a diferença entre eles e a
razão de o arquivo existir assim:

  definir_senha()  - troca a senha sem perguntar quem esta pedindo.
                     Usado pelo criar_primeiro_usuario.py, que roda no
                     terminal, onde não existe usuário logado.

  executar()       - troca a senha a pedido de alguem logado na API.
                     Aqui a permissão e conferida.

Sem essa separação, ou o script do terminal quebraria (não tem como
informar um usuário logado), ou a rota da API ficaria sem checagem - que
era exatamente o problema: qualquer pessoa logada trocava a senha do
Administrador e assumia a conta dele.
"""

from werkzeug.security import generate_password_hash

from extensions import db
from models.usuario import Usuario


class AlterarSenhaService:

    @staticmethod
    def definir_senha(id_usuario, senha_nova):
        """Troca a senha SEM checar permissão.

        Uso interno, fora da API: chamada pelo criar_primeiro_usuario.py,
        que roda no terminal. Quem executa o script já tem acesso ao banco
        e ao código da máquina, entao não ha privilegio a proteger ali.
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
        outra pessoa e privilegio administrativo - sem essa regra, uma
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
