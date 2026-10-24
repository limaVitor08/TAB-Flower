"""
Controller do Cliente.
Só lê a requisição, chama o Service certo e devolve JSON com o código de
status. Regra de negócio e SQL não entram aqui.
"""
from flask import g, jsonify, request
from services.cliente.atualizar_cliente_service import AtualizarClienteService
from services.cliente.buscar_cliente_service import BuscarClienteService
from services.cliente.buscar_clientes_por_nome_service import (
    BuscarClientesPorNomeService,
)
from services.cliente.criar_cliente_service import CriarClienteService
from services.cliente.excluir_cliente_service import ExcluirClienteService
from services.cliente.listar_clientes_service import ListarClientesService
class ClienteController:
    """Recebe as requisições da API de clientes."""
    @staticmethod
    def listar():
        """GET /api/clientes"""
        incluir_inativos = request.args.get("incluir_inativos") == "true"
        clientes = ListarClientesService.executar(
            apenas_ativos=not incluir_inativos
        )
        return jsonify([c.to_dict() for c in clientes]), 200
    @staticmethod
    def buscar_por_nome():
        """GET /api/clientes/busca?nome=silva"""
        try:
            clientes = BuscarClientesPorNomeService.executar(
                request.args.get("nome")
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        # A busca por nome passa por Repository e stored procedure, entao
        # o Service devolve dicionarios prontos, e não objetos Cliente.
        return jsonify(clientes), 200
    @staticmethod
    def buscar_por_documento(documento):
        """GET /api/clientes/documento/12345678901"""
        try:
            cliente = BuscarClienteService.por_documento(documento)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(cliente.to_dict()), 200
    @staticmethod
    def buscar_por_id(id_cliente):
        """GET /api/clientes/1"""
        try:
            cliente = BuscarClienteService.por_id(id_cliente)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(cliente.to_dict()), 200
    @staticmethod
    def criar():
        """POST /api/clientes"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do cliente em JSON."}), 400
        try:
            # Quem cadastrou vem do token, num parâmetro próprio.
            cliente = CriarClienteService.executar(dados, g.usuario_atual.id)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        return jsonify(cliente.to_dict()), 201
    @staticmethod
    def atualizar(id_cliente):
        """PUT /api/clientes/1"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados a alterar em JSON."}), 400
        try:
            cliente = AtualizarClienteService.executar(id_cliente, dados)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(cliente.to_dict()), 200
    @staticmethod
    def excluir(id_cliente):
        """DELETE /api/clientes/1"""
        try:
            ExcluirClienteService.executar(id_cliente, g.usuario_atual)
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify({"mensagem": "Cliente desativado com sucesso."}), 200