"""
Lista os processos que ainda têm documento faltando (funcionalidade 12).
"""

from repositories.processo_repository import ProcessoRepository


class PendenciasService:
    @staticmethod
    def executar(advogado_id=None):
        return ProcessoRepository.pendencias_checklist(advogado_id)
