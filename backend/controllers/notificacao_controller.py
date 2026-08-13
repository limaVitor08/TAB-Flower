"""
Controller da Notificação.

Funcionalidades 16 (Disparo de Notificações) e 17 (Direcionamento
Automático). As notificações são criadas pelo sistema, nunca pelo
usuário - por isso não existe rota de criação aqui.
"""

from flask import g, jsonify, request

from models.notificacao import Notificacao
from repositories.notificacao_repository import NotificacaoRepository


class NotificacaoController:

    @staticmethod
    def listar():
        """GET /api/notificacoes?nao_lidas=true

        Cada pessoa ve apenas os proprios avisos. O destinatario vem do
        token de sessao, nunca da requisicao - antes era possivel pedir
        as notificacoes de qualquer usuario passando o id na URL.
        """
        usuario_id = g.usuario_atual.id
        apenas_nao_lidas = request.args.get("nao_lidas") == "true"

        # Funcionalidades 16 e 17: usa sp_notificacoes_advogado, que traz
        # o contexto (processo, cliente e documento) junto com o aviso.
        avisos = NotificacaoRepository.do_advogado(usuario_id, apenas_nao_lidas)
        return jsonify(avisos), 200

    @staticmethod
    def marcar_lida(id_notificacao):
        """PATCH /api/notificações/1/lida

        Só o destinatário marca o próprio aviso como lido. A listagem já
        filtrava pelo token; era o marcar-lida que faltava conferir. Sem
        isso, alguém marcava como lido o aviso de um colega e ele nunca
        ficava sabendo que havia documento novo no processo dele - o
        oposto do que as Funcionalidades 16 e 17 existem para resolver.
        """
        aviso = Notificacao.buscar_por_id(id_notificacao)
        if not aviso:
            return jsonify({"erro": "Notificação não encontrada."}), 404

        if aviso.usuario_destino_id != g.usuario_atual.id:
            return jsonify({"erro": "Este aviso não é seu."}), 403

        aviso.marcar_lida()
        return jsonify(aviso.to_dict()), 200
