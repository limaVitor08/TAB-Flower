# Recebe os pedidos da tela que configura o checklist de cada tipo de processo
from flask import jsonify, request
from services.checklist.adicionar_item_modelo_service import AdicionarItemModeloService
from services.checklist.alternar_obrigatorio_service import AlternarObrigatorioService
from services.checklist.listar_itens_modelo_service import ListarItensModeloService
from services.checklist.listar_opcoes_checklist_service import ListarOpcoesChecklistService
from services.checklist.remover_item_modelo_service import RemoverItemModeloService
class ChecklistController:
    @staticmethod
    def opcoes():
        opcoes = ListarOpcoesChecklistService.executar()
        return (
            jsonify(
                {
                    "tipos": [t.to_dict() for t in opcoes["tipos"]],
                    "categorias": [c.to_dict() for c in opcoes["categorias"]],
                }
            ),
            200,
        )
    @staticmethod
    def listar():
        tipo_id = request.args.get("tipo_processo_id")
        if not tipo_id:
            return jsonify({"erro": "Informe o tipo_processo_id."}), 400
        try:
            itens = ListarItensModeloService.executar(tipo_id)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(itens), 200
    @staticmethod
    def adicionar():
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do item em JSON."}), 400
        try:
            itens = AdicionarItemModeloService.executar(dados)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        return jsonify(itens), 201
    @staticmethod
    def alternar(id_item):
        try:
            itens = AlternarObrigatorioService.executar(id_item)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(itens), 200
    @staticmethod
    def remover(id_item):
        try:
            itens = RemoverItemModeloService.executar(id_item)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(itens), 200
