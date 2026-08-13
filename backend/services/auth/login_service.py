"""
Caso de uso: autenticar um usuário por e-mail e senha.

Regra de segurança básica: se o e-mail não existe, se a senha está
errada, ou se o usuário está inativo, a mensagem devolvida é sempre a
mesma ("E-mail ou senha inválidos"). Não dizemos qual dos dois errou -
isso evitaria que alguém usasse o formulário de login para descobrir
quais e-mails existem cadastrados no sistema.
"""

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

        # Entrada bem-sucedida vai para o log de auditoria. Só o sucesso:
        # registrar tentativa errada gravaria e-mails digitados por engano,
        # que muitas vezes são a senha de alguém.
        #
        # Aqui o commit e explicito porque o login não altera mais nada no
        # banco - não existe outra gravação para levar o log junto.
        RegistrarAuditoriaService.registrar(
            usuario_id=usuario.id,
            acao="LOGIN",
            entidade="usuario",
            entidade_id=usuario.id,
            descricao=f"{usuario.nome} entrou no sistema.",
        )
        db.session.commit()

        dados_usuario = usuario.to_dict()
        # O pode_excluir vai junto para a interface conhecer o perfil de
        # quem entrou e poder adaptar textos, se um dia precisar.
        #
        # Ele NÃO é usado para esconder botões, e isso é decisão de
        # projeto: os botões de exclusão continuam visíveis para todos, e
        # quem nega é o backend, com uma mensagem explicando a regra. Um
        # botão que some não ensina nada a quem está usando o sistema;
        # "somente o Administrador pode excluir" ensina.
        #
        # De qualquer forma, nada aqui decide permissão. Este valor vive
        # no localStorage e pode ser editado pelo F12 - a decisão é sempre
        # tomada de novo no backend, olhando o perfil real no banco.
        dados_usuario["pode_excluir"] = bool(
            usuario.perfil and usuario.perfil.pode_excluir
        )

        return {"token": token, "usuario": dados_usuario}
