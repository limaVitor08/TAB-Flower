# Recebe o envio, a edição, a exclusão e o download dos documentos
from flask import g, jsonify, request, send_from_directory
from services.documento.atualizar_documento_service import AtualizarDocumentoService
from services.documento.baixar_documento_service import BaixarDocumentoService
from services.documento.buscar_documento_service import BuscarDocumentoService
from services.documento.enviar_documento_service import EnviarDocumentoService
from services.documento.excluir_documento_service import ExcluirDocumentoService
from services.documento.listar_categorias_documento_service import (
    ListarCategoriasDocumentoService,
)
from services.documento.listar_documentos_do_processo_service import (
    ListarDocumentosDoProcessoService,
)
from services.documento.listar_documentos_service import ListarDocumentosService
from services.documento.restaurar_documento_service import RestaurarDocumentoService
class DocumentoController:
    @staticmethod
    def listar():
        incluir_excluidos = request.args.get("incluir_excluidos") == "true"
        processo_id = request.args.get("processo_id")
        if processo_id:
            docs = ListarDocumentosDoProcessoService.executar(
                processo_id, incluir_excluidos
            )
        else:
            docs = ListarDocumentosService.executar(incluir_excluidos)
        return jsonify([d.to_dict() for d in docs]), 200
    @staticmethod
    def categorias():
        categorias = ListarCategoriasDocumentoService.executar()
        return jsonify([c.to_dict() for c in categorias]), 200
    @staticmethod
    def buscar_por_id(id_documento):
        try:
            documento = BuscarDocumentoService.executar(id_documento)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(documento.to_dict()), 200
    @staticmethod
    def enviar():
        arquivo = request.files.get("arquivo")
        try:
            resultado = EnviarDocumentoService.executar(
                arquivo, request.form.to_dict(), g.usuario_atual.id
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        resposta = resultado["documento"].to_dict()
        avanco = resultado["avanco_status"]
        resposta["avanco_status"] = avanco.nome if avanco else None
        return jsonify(resposta), 201
    @staticmethod
    def atualizar(id_documento):
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
        try:
            resultado = ExcluirDocumentoService.executar(
                id_documento, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
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
        try:
            resultado = RestaurarDocumentoService.executar(
                id_documento, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        avanco = resultado["avanco_status"]
        return (
            jsonify(
                {
                    "mensagem": "Documento restaurado com sucesso.",
                    "avanco_status": avanco.nome if avanco else None,
                }
            ),
            200,
        )
    @staticmethod
    def baixar(id_documento):
        try:
            arquivo = BaixarDocumentoService.executar(id_documento)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return send_from_directory(
            arquivo["pasta"],
            arquivo["arquivo"],
            as_attachment=True,
            download_name=arquivo["nome_download"],
        )
