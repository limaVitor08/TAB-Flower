"""
Repository do Processo.

Camada de Persistência Especializada. Todas as consultas deste arquivo
são chamadas a stored procedures do MySQL.
"""

from sqlalchemy import text

from extensions import db
from utils.conversao import converter_linhas


def _linhas(resultado):
    """Converte o retorno da procedure em lista de dicionarios.

    A conversão normaliza datas e valores decimais para o mesmo formato
    usado pelo resto da API.
    """
    return converter_linhas(resultado)


class ProcessoRepository:
    """Consultas específicas do domínio Processo."""

    @staticmethod
    def buscar(termo=None, status_id=None, advogado_id=None, tipo_id=None):
        """Funcionalidade 03 - Busca por Processo.

        Chama sp_buscar_processos. O termo procura ao mesmo tempo no
        número da ação, no título e no nome do cliente. Filtros nulos
        são ignorados pela procedure.
        """
        resultado = db.session.execute(
            text(
                "CALL sp_buscar_processos(:termo, :status_id, "
                ":advogado_id, :tipo_id)"
            ),
            {
                "termo": termo,
                "status_id": status_id,
                "advogado_id": advogado_id,
                "tipo_id": tipo_id,
            },
        )
        return _linhas(resultado)

    @staticmethod
    def painel_resumo():
        """Funcionalidade 06 - Painel Central de Gestao.

        Chama sp_painel_resumo: quantos processos existem em cada fase e
        quantos estao com prazo vencido ou vencendo.
        """
        return _linhas(db.session.execute(text("CALL sp_painel_resumo()")))

    @staticmethod
    def pendencias_checklist(advogado_id=None):
        """Funcionalidade 12 - Mapeamento de Pendências.

        Chama sp_pendencias_checklist. Devolve apenas processos que ainda
        tem documento faltando, com a lista de nomes já montada.
        """
        resultado = db.session.execute(
            text("CALL sp_pendencias_checklist(:advogado_id)"),
            {"advogado_id": advogado_id},
        )
        return _linhas(resultado)

    @staticmethod
    def prioritarios(advogado_id=None, peso_minimo=None):
        """Funcionalidades 14 e 15 - Marcadores e Filtros de Prioridade.

        Chama sp_processos_prioritarios, que ordena por peso do marcador
        e depois por proximidade do prazo.
        """
        resultado = db.session.execute(
            text("CALL sp_processos_prioritarios(:advogado_id, :peso_minimo)"),
            {"advogado_id": advogado_id, "peso_minimo": peso_minimo},
        )
        return _linhas(resultado)
