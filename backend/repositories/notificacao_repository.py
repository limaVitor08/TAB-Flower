"""
Repository da Notificação.

Busca os avisos de um usuário chamando uma stored procedure.
"""

from sqlalchemy import text

from extensions import db
from utils.conversao import converter_linhas


class NotificacaoRepository:

    @staticmethod
    def do_advogado(usuario_id, apenas_nao_lidas=False):
        """Funcionalidades 16 e 17: Notificações com contexto.

        Chama sp_notificacoes_advogado, que junta o aviso ao processo, ao
        cliente e ao documento que o originou. Sem esse JOIN a tela diria
        apenas "novo documento", sem dizer em qual caso.
        """
        resultado = db.session.execute(
            text("CALL sp_notificacoes_advogado(:usuario_id, :nao_lidas)"),
            {"usuario_id": usuario_id, "nao_lidas": apenas_nao_lidas},
        )
        return converter_linhas(resultado)
