"""
Controller do Processo.

Camada de Apresentação. Le a requisição, chama o Service e devolve JSON.
Sem regra de negocio, sem SQL.
"""

from flask import g, jsonify, request

from models.checklist import ChecklistProcesso
from models.processo import HistoricoStatus
from models.tabelas_apoio import StatusProcesso, TipoProcesso
from models.usuario import Usuario
from services.processo.atualizar_processo_service import AtualizarProcessoService
from services.processo.atualizar_status_service import AtualizarStatusService
from services.processo.buscar_processo_service import BuscarProcessoService
from services.processo.buscar_processos_service import BuscarProcessosService
from services.processo.marcadores_service import MarcadoresService
from services.processo.criar_processo_service import CriarProcessoService
from services.processo.excluir_processo_service import ExcluirProcessoService
from services.processo.listar_processos_service import ListarProcessosService


class ProcessoController:
    """Recebe as requisições da API de processos."""

    @staticmethod
    def listar():
        """GET /api/processos"""
        incluir_inativos = request.args.get("incluir_inativos") == "true"
        cliente_id = request.args.get("cliente_id")

        if cliente_id:
            processos = ListarProcessosService.do_cliente(cliente_id)
        else:
            processos = ListarProcessosService.executar(
                apenas_ativos=not incluir_inativos
            )

        return jsonify([p.to_dict() for p in processos]), 200

    @staticmethod
    def buscar_por_id(id_processo):
        """GET /api/processos/1"""
        try:
            processo = BuscarProcessoService.por_id(id_processo)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(processo.to_dict()), 200

    @staticmethod
    def buscar_por_numero():
        """GET /api/processos/número?valor=0001234-56.2026.8.13.0024"""
        try:
            processo = BuscarProcessoService.por_numero(
                request.args.get("valor")
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(processo.to_dict()), 200

    @staticmethod
    def criar():
        """POST /api/processos"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do processo em JSON."}), 400

        try:
            # O autor vai num parâmetro próprio, fora de "dados": assim o
            # Service não tem como confundir o que veio do formulário com
            # quem está logado.
            processo = CriarProcessoService.executar(dados, g.usuario_atual.id)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(processo.to_dict()), 201

    @staticmethod
    def atualizar(id_processo):
        """PUT /api/processos/1"""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados a alterar em JSON."}), 400

        try:
            processo = AtualizarProcessoService.executar(id_processo, dados)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(processo.to_dict()), 200

    @staticmethod
    def atualizar_status(id_processo):
        """PATCH /api/processos/1/status - Funcionalidade 07"""
        dados = request.get_json(silent=True) or {}

        try:
            # Quem mudou a fase vem do token, nunca do corpo da requisição:
            # o histórico só serve para responder "quem mudou isto?" se o
            # autor não puder ser escolhido por quem está mandando o pedido.
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
        """DELETE /api/processos/1"""
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
        """GET /api/processos/1/histórico - Funcionalidade 07"""
        registros = HistoricoStatus.listar_do_processo(id_processo)
        return jsonify([r.to_dict() for r in registros]), 200

    @staticmethod
    def checklist(id_processo):
        """GET /api/processos/1/checklist - Funcionalidades 11 e 12"""
        itens = ChecklistProcesso.listar_do_processo(id_processo)
        return jsonify([i.to_dict() for i in itens]), 200

    @staticmethod
    def buscar():
        """GET /api/processos/busca?termo=&status_id=&advogado_id=&tipo_id=

        Funcionalidade 03. Chama sp_buscar_processos pela camada
        Repository: busca combinada em número, título e nome do cliente,
        com filtros opcionais.
        """
        try:
            linhas = BuscarProcessosService.executar(
                termo=request.args.get("termo"),
                status_id=request.args.get("status_id"),
                advogado_id=request.args.get("advogado_id"),
                tipo_id=request.args.get("tipo_id"),
            )
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(linhas), 200

    @staticmethod
    def listar_marcadores(id_processo):
        """GET /api/processos/1/marcadores - Funcionalidade 14"""
        return jsonify(MarcadoresService.listar_do_processo(id_processo)), 200

    @staticmethod
    def aplicar_marcador(id_processo):
        """POST /api/processos/1/marcadores - Funcionalidade 14"""
        dados = request.get_json(silent=True) or {}

        try:
            # Idem: aplicado_por sai do token, não do JSON enviado.
            marcadores = MarcadoresService.aplicar(
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
        """DELETE /api/processos/1/marcadores/2 - Funcionalidade 14"""
        try:
            marcadores = MarcadoresService.remover(id_processo, id_marcador)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(marcadores), 200

    @staticmethod
    def opcoes():
        """GET /api/processos/opções

        Devolve numa única chamada tudo que os selects do formulario
        precisam. Sem isso, a tela faria três requisições só para abrir.
        """
        return (
            jsonify(
                {
                    "tipos": [t.to_dict() for t in TipoProcesso.listar_todos()],
                    "status": [s.to_dict() for s in StatusProcesso.listar_todos()],
                    "advogados": [a.to_dict() for a in Usuario.listar_advogados()],
                }
            ),
            200,
        )
