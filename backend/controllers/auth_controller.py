"""
Controller de autenticação.

Camada de Apresentação. A rota de login é a única rota da API que fica
pública - todas as outras exigem o token que ela devolve.
"""

from flask import g, jsonify, request

from services.auth.login_service import LoginService


class AuthController:
    """Recebe as requisições de login."""

    @staticmethod
    def login():
        """POST /api/auth/login"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie e-mail e senha em JSON."}), 400

        try:
            resultado = LoginService.executar(
                dados.get("email"), dados.get("senha")
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 401

        return jsonify(resultado), 200

    @staticmethod
    def eu():
        """GET /api/usuarios/eu

        Devolve os dados de quem está logado, a partir do token - não
        de nenhum parâmetro da requisição. Usado pelo frontend para
        exibir o nome/perfil no cabeçalho e reconhecer sessão salva.
        """
        dados_usuario = g.usuario_atual.to_dict()
        dados_usuario["pode_excluir"] = bool(
            g.usuario_atual.perfil and g.usuario_atual.perfil.pode_excluir
        )
        return jsonify(dados_usuario), 200
