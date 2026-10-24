"""Lista os processos por ordem de urgência (funcionalidades 14 e 15)."""

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
