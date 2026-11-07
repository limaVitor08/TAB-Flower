# Recebe os pedidos do painel de gestão
from flask import jsonify, request

from services.painel.listar_marcadores_service import ListarMarcadoresService
from services.painel.pendencias_service import PendenciasService
from services.painel.processos_prioritarios_service import (
    ProcessosPrioritariosService,
)
from services.painel.resumo_painel_service import ResumoPainelService


class PainelController:

    @staticmethod
    def resumo():
        return jsonify(ResumoPainelService.executar()), 200

    @staticmethod
    def pendencias():
        advogado_id = request.args.get("advogado_id") or None
        return jsonify(PendenciasService.executar(advogado_id)), 200

    @staticmethod
    def prioritarios():
        try:
            linhas = ProcessosPrioritariosService.executar(
                request.args.get("advogado_id") or None,
                request.args.get("peso_minimo") or None,
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(linhas), 200

    @staticmethod
    def marcadores():
        marcadores = ListarMarcadoresService.executar()
        return jsonify([m.to_dict() for m in marcadores]), 200
