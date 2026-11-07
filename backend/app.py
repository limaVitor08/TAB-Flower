# Monta a aplicação Flask com banco, log, CORS, rotas e tratamento de erros
import logging
import os
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from config import Config
from extensions import db
ARQUIVO_DE_LOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tabflower.log"
)
NOME_DO_LOGGER = "tabflower"
def configurar_log():
    logger = logging.getLogger(NOME_DO_LOGGER)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    destino = logging.FileHandler(ARQUIVO_DE_LOG, encoding="utf-8")
    destino.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(destino)
    return logger
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    logger = configurar_log()
    if Config.SECRET_KEY == "chave-de-desenvolvimento":
        logger.warning(
            "SECRET_KEY esta no valor padrao. Gere uma chave propria no .env: "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    db.init_app(app)
    CORS(
        app,
        origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
    )
    from routes import registrar_rotas
    registrar_rotas(app)
    _registrar_tratadores_de_erro(app)
    return app
def _registrar_tratadores_de_erro(app):
    @app.errorhandler(400)
    def erro_requisicao_invalida(erro):
        return jsonify({"erro": "Requisição inválida"}), 400
    @app.errorhandler(404)
    def erro_nao_encontrado(erro):
        return jsonify({"erro": "Recurso não encontrado"}), 404
    @app.errorhandler(405)
    def erro_metodo_nao_permitido(erro):
        return jsonify({"erro": "Método não permitido para esta rota"}), 405
    @app.errorhandler(413)
    def erro_arquivo_grande(erro):
        limite_mb = Config.MAX_CONTENT_LENGTH // (1024 * 1024)
        return jsonify({"erro": f"O arquivo passa do limite de {limite_mb} MB."}), 413
    @app.errorhandler(HTTPException)
    def erro_http(erro):
        return (
            jsonify({"erro": erro.description or "Erro na requisição."}),
            erro.code or 500,
        )
    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        db.session.rollback()
        logging.getLogger(NOME_DO_LOGGER).exception("Erro inesperado no servidor")
        return jsonify({"erro": "Erro inesperado no servidor."}), 500
