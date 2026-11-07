# Recebe os pedidos dos avisos de quem está logado
from flask import g, jsonify, request
from services.notificacao.listar_notificacoes_service import ListarNotificacoesService
from services.notificacao.marcar_notificacao_lida_service import (
    MarcarNotificacaoLidaService,
)
class NotificacaoController:
    @staticmethod
    def listar():
        apenas_nao_lidas = request.args.get("nao_lidas") == "true"
        avisos = ListarNotificacoesService.executar(
            g.usuario_atual.id, apenas_nao_lidas
        )
        return jsonify(avisos), 200
    @staticmethod
    def marcar_lida(id_notificacao):
        try:
            aviso = MarcarNotificacaoLidaService.executar(
                id_notificacao, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        return jsonify(aviso.to_dict()), 200
