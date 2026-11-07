# Recebe os pedidos de clientes e repassa cada um ao Service certo
from flask import g, jsonify, request
from services.cliente.atualizar_cliente_service import AtualizarClienteService
from services.cliente.buscar_cliente_por_documento_service import (
    BuscarClientePorDocumentoService,
)
from services.cliente.buscar_cliente_service import BuscarClienteService
from services.cliente.buscar_clientes_por_nome_service import (
    BuscarClientesPorNomeService,
)
from services.cliente.criar_cliente_service import CriarClienteService
from services.cliente.excluir_cliente_service import ExcluirClienteService
from services.cliente.listar_clientes_service import ListarClientesService
class ClienteController:
    @staticmethod
    def listar():
        incluir_inativos = request.args.get("incluir_inativos") == "true"
        clientes = ListarClientesService.executar(
            apenas_ativos=not incluir_inativos
        )
        return jsonify([c.to_dict() for c in clientes]), 200
    @staticmethod
    def buscar_por_nome():
        incluir_inativos = request.args.get("incluir_inativos") == "true"
        try:
            clientes = BuscarClientesPorNomeService.executar(
                request.args.get("nome"), apenas_ativos=not incluir_inativos
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        return jsonify(clientes), 200
    @staticmethod
    def buscar_por_documento(documento):
        try:
            cliente = BuscarClientePorDocumentoService.executar(documento)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(cliente.to_dict()), 200
    @staticmethod
    def buscar_por_id(id_cliente):
        try:
            cliente = BuscarClienteService.executar(id_cliente)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(cliente.to_dict()), 200
    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do cliente em JSON."}), 400
        try:
            cliente = CriarClienteService.executar(dados, g.usuario_atual.id)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        return jsonify(cliente.to_dict()), 201
    @staticmethod
    def atualizar(id_cliente):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados a alterar em JSON."}), 400
        try:
            cliente = AtualizarClienteService.executar(
                id_cliente, dados, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(cliente.to_dict()), 200
    @staticmethod
    def excluir(id_cliente):
        try:
            ExcluirClienteService.executar(id_cliente, g.usuario_atual)
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify({"mensagem": "Cliente desativado com sucesso."}), 200
