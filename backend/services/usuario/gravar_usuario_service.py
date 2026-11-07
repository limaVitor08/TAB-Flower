# Valida e grava um usuário novo com a senha protegida por hash
from datetime import datetime

from werkzeug.security import generate_password_hash

from extensions import db
from models.usuario import Perfil, Usuario


class GravarUsuarioService:

    @staticmethod
    def executar(dados):
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
