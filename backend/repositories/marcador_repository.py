# Guarda e consulta os marcadores aplicados em cada processo
from datetime import datetime

from sqlalchemy import text

from extensions import db
from utils.conversao import converter_linhas


class MarcadorRepository:

    @staticmethod
    def listar_do_processo(processo_id):
        resultado = db.session.execute(
            text(
                "SELECT m.id, m.nome, m.cor_hex, m.peso "
                "FROM processo_marcador pm "
                "INNER JOIN marcador m ON m.id = pm.marcador_id "
                "WHERE pm.processo_id = :pid "
                "ORDER BY m.peso DESC"
            ),
            {"pid": processo_id},
        )
        return converter_linhas(resultado)

    @staticmethod
    def esta_aplicado(processo_id, marcador_id):
        linha = db.session.execute(
            text(
                "SELECT 1 FROM processo_marcador "
                "WHERE processo_id = :pid AND marcador_id = :mid"
            ),
            {"pid": processo_id, "mid": marcador_id},
        ).first()
        return linha is not None

    @staticmethod
    def aplicar(processo_id, marcador_id, usuario_id=None):
        db.session.execute(
            text(
                "INSERT INTO processo_marcador "
                "(processo_id, marcador_id, aplicado_por, aplicado_em) "
                "VALUES (:pid, :mid, :uid, :quando)"
            ),
            {
                "pid": processo_id,
                "mid": marcador_id,
                "uid": usuario_id,
                "quando": datetime.now(),
            },
        )

    @staticmethod
    def remover(processo_id, marcador_id):
        resultado = db.session.execute(
            text(
                "DELETE FROM processo_marcador "
                "WHERE processo_id = :pid AND marcador_id = :mid"
            ),
            {"pid": processo_id, "mid": marcador_id},
        )
        return resultado.rowcount
