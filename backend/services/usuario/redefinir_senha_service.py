# Troca a senha sem conferir permissão, usado pelo terminal
from werkzeug.security import generate_password_hash

from extensions import db
from models.usuario import Usuario


class RedefinirSenhaService:

    @staticmethod
    def executar(id_usuario, senha_nova):
        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")

        senha_nova = senha_nova or ""

        if len(senha_nova) < 6:
            raise ValueError("A senha precisa ter ao menos 6 caracteres.")

        usuario.senha_hash = generate_password_hash(senha_nova)
        db.session.commit()

        return usuario
