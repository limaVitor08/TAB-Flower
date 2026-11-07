# Busca os avisos de um usuário usando uma stored procedure
from sqlalchemy import text

from extensions import db
from utils.conversao import converter_linhas


class NotificacaoRepository:

    @staticmethod
    def do_advogado(usuario_id, apenas_nao_lidas=False):
        resultado = db.session.execute(
            text("CALL sp_notificacoes_advogado(:usuario_id, :nao_lidas)"),
            {"usuario_id": usuario_id, "nao_lidas": apenas_nao_lidas},
        )
        return converter_linhas(resultado)
