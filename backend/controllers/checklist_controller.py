"""
Controller da configuração de checklist (funcionalidade 13).
Lê a requisição, chama o Service e devolve JSON.
"""
from flask import jsonify, request
from models.tabelas_apoio import CategoriaDocumento, TipoProcesso
from services.checklist.gerenciar_modelo_service import GerenciarModeloService
class ChecklistController:
    @staticmethod
    def opcoes():
        """GET /api/checklists/opcoes - tipos e categorias para a tela."""
        return (
            jsonify(
                {
                    "tipos": [t.to_dict() for t in TipoProcesso.listar_todos()],
                    "categorias": [
                        c.to_dict() for c in CategoriaDocumento.listar_todos()
                    ],
                }
            ),
            200,
        )
    @staticmethod
    def listar():
        """GET /api/checklists?tipo_processo_id=1"""
        tipo_id = request.args.get("tipo_processo_id")
        if not tipo_id:
            return jsonify({"erro": "Informe o tipo_processo_id."}), 400
        try:
            itens = GerenciarModeloService.listar(tipo_id)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(itens), 200
    @staticmethod
    def adicionar():
        """POST /api/checklists"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do item em JSON."}), 400
        try:
            itens = GerenciarModeloService.adicionar(dados)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        return jsonify(itens), 201
    @staticmethod
    def alternar(id_item):
        """PATCH /api/checklists/1/obrigatorio"""
        try:
            itens = GerenciarModeloService.alternar_obrigatorio(id_item)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(itens), 200
    @staticmethod
    def remover(id_item):
        """DELETE /api/checklists/1"""
        try:
            itens = GerenciarModeloService.remover(id_item)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(itens), 200