# Recebe os pedidos de processos, fases e marcadores
from flask import g, jsonify, request

from services.processo.aplicar_marcador_service import AplicarMarcadorService
from services.processo.atualizar_processo_service import AtualizarProcessoService
from services.processo.atualizar_status_service import AtualizarStatusService
from services.processo.buscar_processo_service import BuscarProcessoService
from services.processo.buscar_processos_service import BuscarProcessosService
from services.processo.criar_processo_service import CriarProcessoService
from services.processo.excluir_processo_service import ExcluirProcessoService
from services.processo.listar_checklist_do_processo_service import (
    ListarChecklistDoProcessoService,
)
from services.processo.listar_historico_service import ListarHistoricoService
from services.processo.listar_marcadores_do_processo_service import (
    ListarMarcadoresDoProcessoService,
)
from services.processo.listar_opcoes_processo_service import (
    ListarOpcoesProcessoService,
)
from services.processo.listar_processos_service import ListarProcessosService
from services.processo.remover_marcador_service import RemoverMarcadorService


class ProcessoController:
    @staticmethod
    def listar():
        incluir_inativos = request.args.get("incluir_inativos") == "true"
        processos = ListarProcessosService.executar(
            apenas_ativos=not incluir_inativos
        )

        return jsonify([p.to_dict() for p in processos]), 200

    @staticmethod
    def buscar_por_id(id_processo):
        try:
            processo = BuscarProcessoService.executar(id_processo)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(processo.to_dict()), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do processo em JSON."}), 400

        try:
            processo = CriarProcessoService.executar(dados, g.usuario_atual.id)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(processo.to_dict()), 201

    @staticmethod
    def atualizar(id_processo):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados a alterar em JSON."}), 400

        try:
            processo = AtualizarProcessoService.executar(
                id_processo, dados, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(processo.to_dict()), 200

    @staticmethod
    def atualizar_status(id_processo):
        dados = request.get_json(silent=True) or {}

        try:
            processo = AtualizarStatusService.executar(
                id_processo,
                dados.get("status_id"),
                g.usuario_atual.id,
                dados.get("observacao"),
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(processo.to_dict()), 200

    @staticmethod
    def excluir(id_processo):
        try:
            ExcluirProcessoService.executar(id_processo, g.usuario_atual)
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify({"mensagem": "Processo arquivado com sucesso."}), 200

    @staticmethod
    def historico(id_processo):
        registros = ListarHistoricoService.executar(id_processo)
        return jsonify([r.to_dict() for r in registros]), 200

    @staticmethod
    def checklist(id_processo):
        itens = ListarChecklistDoProcessoService.executar(id_processo)
        return jsonify([i.to_dict() for i in itens]), 200

    @staticmethod
    def buscar():
        try:
            linhas = BuscarProcessosService.executar(
                termo=request.args.get("termo"),
                status_id=request.args.get("status_id"),
                advogado_id=request.args.get("advogado_id"),
                tipo_id=request.args.get("tipo_id"),
                incluir_arquivados=request.args.get("incluir_inativos") == "true",
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(linhas), 200

    @staticmethod
    def listar_marcadores(id_processo):
        marcadores = ListarMarcadoresDoProcessoService.executar(id_processo)
        return jsonify(marcadores), 200

    @staticmethod
    def aplicar_marcador(id_processo):
        dados = request.get_json(silent=True) or {}

        try:
            marcadores = AplicarMarcadorService.executar(
                id_processo,
                dados.get("marcador_id"),
                g.usuario_atual.id,
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(marcadores), 201

    @staticmethod
    def remover_marcador(id_processo, id_marcador):
        try:
            marcadores = RemoverMarcadorService.executar(id_processo, id_marcador)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(marcadores), 200

    @staticmethod
    def opcoes():
        opcoes = ListarOpcoesProcessoService.executar()
        return (
            jsonify(
                {
                    "tipos": [t.to_dict() for t in opcoes["tipos"]],
                    "status": [s.to_dict() for s in opcoes["status"]],
                    "advogados": [a.to_dict() for a in opcoes["advogados"]],
                }
            ),
            200,
        )
