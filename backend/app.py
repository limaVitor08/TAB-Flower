"""
Fabrica da aplicação Flask (padrão Application Factory).

A função create_app() monta a aplicação: carrega a configuração, liga o
registro de erros em arquivo, conecta o SQLAlchemy, libera o CORS para o
frontend e registra as rotas.
"""

import logging
import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from flask_cors import CORS

from config import Config
from extensions import db

# Nome do arquivo onde os erros são gravados, ao lado do run.py.
ARQUIVO_DE_LOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tabflower.log"
)

# Único logger do projeto. Todo Service que precisa registrar um erro faz
# "logging.getLogger('tabflower')" e usa este mesmo canal - do mesmo jeito
# que todo mundo importa o mesmo "db" de extensions.py.
NOME_DO_LOGGER = "tabflower"


def configurar_log():
    """Liga o registro de erros em arquivo.

    Sem isso, todo erro capturado por um "except" desaparecia sem deixar
    rastro: o usuário via a mensagem amigável na tela e ninguem ficava
    sabendo o que realmente aconteceu. Agora a mensagem amigável continua
    indo para a tela, e o motivo tecnico fica gravado em tabflower.log.

    Usamos o modulo "logging" da biblioteca padrão do Python - nenhuma
    dependencia nova entra no requirements.txt por causa disto.
    """
    logger = logging.getLogger(NOME_DO_LOGGER)

    # create_app() pode ser chamada mais de uma vez (o run.py em modo debug
    # recarrega a aplicação a cada arquivo salvo). Sem esta guarda, cada
    # recarga acrescentaria mais um destino e a mesma linha apareceria
    # repetida no arquivo.
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
    """Cria e devolve a aplicação Flask configurada."""
    app = Flask(__name__)
    app.config.from_object(Config)

    logger = configurar_log()

    # A SECRET_KEY assina os tokens de sessão. Se ela ficar no valor padrão
    # do config.py (porque o .env nao foi criado), qualquer pessoa que
    # conheca esse valor consegue forjar um token de Administrador. A API
    # sobe assim mesmo para nao travar o desenvolvimento, mas o aviso fica
    # registrado.
    if Config.SECRET_KEY == "chave-de-desenvolvimento":
        logger.warning(
            "SECRET_KEY esta no valor padrao. Gere uma chave propria no .env: "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Conecta a instância única do SQLAlchemy a esta aplicação.
    db.init_app(app)

    # Libera o frontend (que roda em outra porta) a chamar a API.
    #
    # Antes aqui era apenas CORS(app), que aceita requisição de QUALQUER
    # site. Como agora existe login, uma página maliciosa aberta no mesmo
    # navegador poderia disparar chamadas à API. Restringindo a origem,
    # só o frontend do TabFlower consegue conversar com o backend.
    #
    # As portas abaixo são as do Live Preview do VS Code. Se você usar
    # outra ferramenta para servir o frontend (Live Server usa a 5500),
    # acrescente a porta correspondente nesta lista.
    CORS(
        app,
        origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
    )

    # Registra as rotas de todos os modulos.
    from routes import registrar_rotas

    registrar_rotas(app)

    _registrar_tratadores_de_erro(app)

    return app


def _registrar_tratadores_de_erro(app):
    """Garante que a API sempre responda JSON, inclusive nos erros.

    Sem isso, um erro faz o Flask devolver uma página HTML e o JavaScript
    do frontend quebra ao tentar ler a resposta como JSON - o usuário via
    "Unexpected token '<'" na tela, que não diz nada a ninguem.

    Os tratadores abaixo vão do mais específico para o mais geral. O Flask
    sempre escolhe o mais específico que serve para aquele erro.
    """

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
        """Rede de segurança para os demais erros de HTTP.

        Preserva o código original: um 401 continua 401, um 415 continua
        415. Transformar tudo em 500 esconderia do frontend o que de fato
        aconteceu - e o api.js decide o que fazer justamente pelo código
        (401, por exemplo, manda a pessoa de volta para o login).
        """
        return (
            jsonify({"erro": erro.description or "Erro na requisição."}),
            erro.code or 500,
        )

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        """Última rede: qualquer exceção que ninguém tratou.

        Duas coisas acontecem aqui, e as duas importam:

        1. O rollback devolve a sessão do banco a um estado limpo. Sem
           ele, a requisição seguinte herdaria a transação quebrada desta.

        2. O motivo técnico vai para o tabflower.log, e o usuário recebe
           uma frase genérica. A mensagem de uma exceção pode conter nome
           de tabela, trecho de SQL ou caminho de arquivo do servidor -
           nada disso deve aparecer na tela.
        """
        db.session.rollback()
        logging.getLogger(NOME_DO_LOGGER).exception("Erro inesperado no servidor")
        return jsonify({"erro": "Erro inesperado no servidor."}), 500
