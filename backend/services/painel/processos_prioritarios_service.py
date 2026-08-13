"""
Caso de uso: listar os processos por ordem de urgencia.

Funcionalidade 14 - Marcadores Visuais.
Funcionalidade 15 - Filtros de Prioridade.
"""

from repositories.processo_repository import ProcessoRepository


class ProcessosPrioritariosService:
    @staticmethod
    def executar(advogado_id=None, peso_minimo=None):
        if peso_minimo is not None:
            try:
                peso_minimo = int(peso_minimo)
            except (TypeError, ValueError):
                raise ValueError("O peso mínimo precisa ser um número.")

        return ProcessoRepository.prioritarios(advogado_id, peso_minimo)
