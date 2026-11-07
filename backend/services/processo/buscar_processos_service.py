# Busca processos por termo e filtros
from repositories.processo_repository import ProcessoRepository


class BuscarProcessosService:
    @staticmethod
    def executar(termo=None, status_id=None, advogado_id=None, tipo_id=None,
                 incluir_arquivados=False):
        termo = (termo or "").strip() or None

        if termo and len(termo) < 2:
            raise ValueError("Digite ao menos 2 caracteres para buscar.")

        return ProcessoRepository.buscar(
            termo=termo,
            status_id=_inteiro(status_id),
            advogado_id=_inteiro(advogado_id),
            tipo_id=_inteiro(tipo_id),
            incluir_arquivados=incluir_arquivados,
        )


def _inteiro(valor):
    if valor in (None, "", "null"):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None
