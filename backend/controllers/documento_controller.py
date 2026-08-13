"""
Controller do Documento.

Camada de Apresentação.

Este Controller e o único que recebe multipart/form-data em vez de JSON,
porque e por onde o arquivo sobe. Mesmo assim a regra continua: ele só
le a requisição e chama o Service.
"""

import os

from flask import g, jsonify, request, send_from_directory

from config import Config
from models.tabelas_apoio import CategoriaDocumento
from services.documento.atualizar_documento_service import AtualizarDocumentoService
from services.documento.buscar_documento_service import BuscarDocumentoService
from services.documento.enviar_documento_service import EnviarDocumentoService
from services.documento.excluir_documento_service import ExcluirDocumentoService
from services.documento.listar_documentos_service import ListarDocumentosService


class DocumentoController:
    """Recebe as requisições da API de documentos."""

    @staticmethod
    def listar():
        """GET /api/documentos"""
        incluir_excluidos = request.args.get("incluir_excluidos") == "true"
        processo_id = request.args.get("processo_id")
        cliente_id = request.args.get("cliente_id")

        if processo_id:
            docs = ListarDocumentosService.do_processo(processo_id, incluir_excluidos)
        elif cliente_id:
            docs = ListarDocumentosService.do_cliente(cliente_id, incluir_excluidos)
        else:
            docs = ListarDocumentosService.executar(incluir_excluidos)

        return jsonify([d.to_dict() for d in docs]), 200

    @staticmethod
    def categorias():
        """GET /api/documentos/categorias - alimenta o select da tela."""
        return (
            jsonify([c.to_dict() for c in CategoriaDocumento.listar_todos()]),
            200,
        )

    @staticmethod
    def buscar_por_id(id_documento):
        """GET /api/documentos/1"""
        try:
            documento = BuscarDocumentoService.por_id(id_documento)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(documento.to_dict()), 200

    @staticmethod
    def enviar():
        """POST /api/documentos

        Recebe multipart/form-data: o arquivo no campo "arquivo" e os
        demais dados como campos de formulario.
        """
        arquivo = request.files.get("arquivo")

        # Quem enviou vai num parâmetro separado, direto de g.usuario_atual.
        # Assim o Service nunca precisa procurar o autor dentro do
        # formulário - e um "enviado_por" que venha na requisição
        # simplesmente não é lido por ninguém.
        try:
            resultado = EnviarDocumentoService.executar(
                arquivo, request.form.to_dict(), g.usuario_atual.id
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        resposta = resultado["documento"].to_dict()

        # A tela precisa saber se o processo mudou de fase por conta deste
        # anexo, para avisar quem enviou. Automação silenciosa assusta
        # quem está operando o sistema.
        avanco = resultado["avanco_status"]
        resposta["avanco_status"] = avanco.nome if avanco else None

        return jsonify(resposta), 201

    @staticmethod
    def atualizar(id_documento):
        """PUT /api/documentos/1"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados a alterar em JSON."}), 400

        try:
            documento = AtualizarDocumentoService.executar(id_documento, dados)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(documento.to_dict()), 200

    @staticmethod
    def excluir(id_documento):
        """DELETE /api/documentos/1"""
        try:
            resultado = ExcluirDocumentoService.executar(
                id_documento, g.usuario_atual
            )
        except PermissionError as erro:
            # 403: o pedido esta correto, mas o usuário não tem permissão.
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        # Se a exclusão reabriu uma pendência, o processo pode ter voltado
        # para a fase anterior. A tela avisa quem excluiu.
        retorno = resultado["retorno_status"]

        return (
            jsonify(
                {
                    "mensagem": "Documento excluído com sucesso.",
                    "retorno_status": retorno.nome if retorno else None,
                }
            ),
            200,
        )

    @staticmethod
    def restaurar(id_documento):
        """PATCH /api/documentos/1/restaurar"""
        try:
            ExcluirDocumentoService.restaurar(id_documento, g.usuario_atual)
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify({"mensagem": "Documento restaurado com sucesso."}), 200

    @staticmethod
    def baixar(id_documento):
        """GET /api/documentos/1/arquivo - devolve o arquivo em si."""
        try:
            documento = BuscarDocumentoService.por_id(id_documento)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        if documento.excluido:
            return jsonify({"erro": "Este documento foi excluído."}), 404

        caminho = os.path.join(Config.PASTA_ARQUIVOS, documento.caminho_arquivo)

        if not os.path.exists(caminho):
            return (
                jsonify({"erro": "O arquivo não foi encontrado no servidor."}),
                404,
            )

        return send_from_directory(
            os.path.dirname(caminho),
            os.path.basename(caminho),
            as_attachment=True,
            download_name=documento.nome_padronizado,
        )
