# Recebe o login e devolve o token de acesso
from flask import jsonify, request
from services.auth.login_service import LoginService
class AuthController:
    @staticmethod
    def login():
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
