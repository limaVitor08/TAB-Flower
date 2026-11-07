# Responde se a API está no ar e se o banco está conectado
from flask import jsonify

from services.sistema.verificar_conexao_service import VerificarConexaoService


class SistemaController:

    @staticmethod
    def status():
        try:
            resultado = VerificarConexaoService.executar()
        except ConnectionError:
            return jsonify({"api": "no ar", "banco": "sem conexão"}), 500

        return jsonify(resultado), 200
