# Recebe a planilha da importação e os pedidos para desfazer um lote
from flask import Response, g, jsonify, request

from services.importacao.desfazer_importacao_service import (
    DesfazerImportacaoService,
)
from services.importacao.gerar_modelo_importacao_service import (
    GerarModeloImportacaoService,
)
from services.importacao.importar_clientes_service import ImportarClientesService
from services.importacao.listar_clientes_do_lote_service import (
    ListarClientesDoLoteService,
)
from services.importacao.listar_importacoes_service import ListarImportacoesService


class ImportacaoController:

    @staticmethod
    def listar():
        lotes = ListarImportacoesService.executar()
        return jsonify([l.to_dict() for l in lotes]), 200

    @staticmethod
    def clientes(id_importacao):
        try:
            clientes = ListarClientesDoLoteService.executar(id_importacao)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify([c.to_dict() for c in clientes]), 200

    @staticmethod
    def importar():
        arquivo = request.files.get("arquivo")

        try:
            lote = ImportarClientesService.executar(
                arquivo, g.usuario_atual.id
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(lote.to_dict()), 201

    @staticmethod
    def desfazer(id_importacao):
        try:
            resultado = DesfazerImportacaoService.executar(
                id_importacao, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(resultado), 200

    @staticmethod
    def modelo():
        conteudo = GerarModeloImportacaoService.executar()

        return Response(
            conteudo,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    "attachment; filename=modelo_importacao_clientes.csv"
            },
        )
