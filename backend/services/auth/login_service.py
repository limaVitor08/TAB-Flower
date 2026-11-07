# Confere email e senha e entrega o token de quem entrou
from werkzeug.security import check_password_hash
from extensions import db
from models.usuario import Usuario
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)
from utils.token import gerar_token
class LoginService:
    @staticmethod
    def executar(email, senha):
        email = (email or "").strip().lower()
        senha = senha or ""
        if not email or not senha:
            raise ValueError("Informe e-mail e senha.")
        usuario = Usuario.buscar_por_email(email)
        if (
            not usuario
            or not usuario.ativo
            or not check_password_hash(usuario.senha_hash, senha)
        ):
            raise ValueError("E-mail ou senha inválidos.")
        token = gerar_token(usuario.id)
        RegistrarAuditoriaService.executar(
            usuario_id=usuario.id,
            acao="LOGIN",
            entidade="usuario",
            entidade_id=usuario.id,
            descricao=f"{usuario.nome} entrou no sistema.",
        )
        db.session.commit()
        dados_usuario = usuario.to_dict()
        dados_usuario["pode_excluir"] = bool(
            usuario.perfil and usuario.perfil.pode_excluir
        )
        return {"token": token, "usuario": dados_usuario}
