"""
Controller da importação em lote.

Funcionalidades 18 e 19. Recebe a planilha em multipart/form-data,
chama o Service e devolve o resultado da carga.
"""

import csv
import io

from flask import Response, g, jsonify, request

from services.importacao.desfazer_importacao_service import (
    DesfazerImportacaoService,
)
from services.importacao.importar_clientes_service import ImportarClientesService
from services.importacao.listar_importacoes_service import ListarImportacoesService


class ImportacaoController:

    @staticmethod
    def listar():
        """GET /api/importacoes"""
        lotes = ListarImportacoesService.executar()
        return jsonify([l.to_dict() for l in lotes]), 200

    @staticmethod
    def clientes(id_importacao):
        """GET /api/importacoes/1/clientes"""
        try:
            clientes = ListarImportacoesService.clientes_do_lote(id_importacao)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify([c.to_dict() for c in clientes]), 200

    @staticmethod
    def importar():
        """POST /api/importacoes - recebe a planilha."""
        arquivo = request.files.get("arquivo")

        try:
            # Quem importou vem do token, nao do formulario: assim o
            # lote fica corretamente atribuido a quem de fato executou.
            lote = ImportarClientesService.executar(
                arquivo, g.usuario_atual.id
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(lote.to_dict()), 201

    @staticmethod
    def desfazer(id_importacao):
        """DELETE /api/importacoes/1"""
        try:
            resultado = DesfazerImportacaoService.executar(
                id_importacao, g.usuario_atual
            )
        except PermissionError as erro:
            # 403: desfazer uma carga desativa varios clientes de uma vez,
            # entao vale a mesma trava da exclusão de cliente pela tela.
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(resultado), 200

    @staticmethod
    def modelo():
        """GET /api/importacoes/modelo

        Devolve um CSV de exemplo, já com as colunas certas e duas linhas
        preenchidas. Sem isso, a secretária teria que adivinhar o formato.
        """
        saida = io.StringIO()
        escritor = csv.writer(saida, delimiter=";")

        escritor.writerow(
            ["nome", "tipo_pessoa", "documento", "email",
             "telefone", "endereco", "cidade", "estado", "observacao"]
        )
        escritor.writerow(
            ["Maria da Silva", "F", "529.982.247-25", "maria@exemplo.com",
             "(31) 99999-8888", "Rua das Flores, 100", "Belo Horizonte", "MG",
             "Cliente antiga, pasta fisica no armario 3"]
        )
        escritor.writerow(
            ["Silva Comercio LTDA", "J", "11.222.333/0001-81", "contato@silva.com",
             "(31) 3333-4444", "Av. Afonso Pena, 500", "Belo Horizonte", "MG", ""]
        )

        # BOM para o Excel abrir com acento correto.
        conteudo = "\ufeff" + saida.getvalue()

        return Response(
            conteudo,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    "attachment; filename=modelo_importacao_clientes.csv"
            },
        )
