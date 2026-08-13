"""
Controller do Painel.

Camada de Apresentação das funcionalidades da Terceira Etapa. Todas as
rotas deste Controller passam por Services que usam Repository, e todo
Repository chama uma stored procedure do MySQL.
"""

from flask import jsonify, request

from models.tabelas_apoio import Marcador
from services.painel.pendencias_service import PendenciasService
from services.painel.processos_prioritarios_service import (
    ProcessosPrioritariosService,
)
from services.painel.resumo_painel_service import ResumoPainelService


class PainelController:

    @staticmethod
    def resumo():
        """GET /api/painel/resumo - sp_painel_resumo"""
        return jsonify(ResumoPainelService.executar()), 200

    @staticmethod
    def pendencias():
        """GET /api/painel/pendências?advogado_id= - sp_pendencias_checklist"""
        advogado_id = request.args.get("advogado_id") or None
        return jsonify(PendenciasService.executar(advogado_id)), 200

    @staticmethod
    def prioritarios():
        """GET /api/painel/prioritarios?peso_minimo=1 - sp_processos_prioritarios"""
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
        """GET /api/painel/marcadores - marcadores fixos do sistema."""
        return jsonify([m.to_dict() for m in Marcador.listar_todos()]), 200
