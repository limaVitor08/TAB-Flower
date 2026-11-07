# Busca processos e monta os números do painel usando stored procedures
from sqlalchemy import text

from extensions import db
from utils.conversao import converter_linhas


def _linhas(resultado):
    return converter_linhas(resultado)


class ProcessoRepository:
    @staticmethod
    def buscar(termo=None, status_id=None, advogado_id=None, tipo_id=None,
               incluir_arquivados=False):
        resultado = db.session.execute(
            text(
                "CALL sp_buscar_processos(:termo, :status_id, "
                ":advogado_id, :tipo_id, :incluir_arquivados)"
            ),
            {
                "termo": termo,
                "status_id": status_id,
                "advogado_id": advogado_id,
                "tipo_id": tipo_id,
                "incluir_arquivados": bool(incluir_arquivados),
            },
        )
        return _linhas(resultado)

    @staticmethod
    def painel_resumo():
        return _linhas(db.session.execute(text("CALL sp_painel_resumo()")))

    @staticmethod
    def pendencias_checklist(advogado_id=None):
        resultado = db.session.execute(
            text("CALL sp_pendencias_checklist(:advogado_id)"),
            {"advogado_id": advogado_id},
        )
        return _linhas(resultado)

    @staticmethod
    def prioritarios(advogado_id=None, peso_minimo=None):
        resultado = db.session.execute(
            text("CALL sp_processos_prioritarios(:advogado_id, :peso_minimo)"),
            {"advogado_id": advogado_id, "peso_minimo": peso_minimo},
        )
        return _linhas(resultado)
