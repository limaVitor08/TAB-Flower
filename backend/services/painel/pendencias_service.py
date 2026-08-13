"""
Caso de uso: listar os processos com documentação incompleta.

Funcionalidade 12 - Mapeamento de Pendências.

Substitui o checklist impresso e o "vou dar uma olhada nas pastas".
"""

from repositories.processo_repository import ProcessoRepository


class PendenciasService:
    @staticmethod
    def executar(advogado_id=None):
        return ProcessoRepository.pendencias_checklist(advogado_id)
