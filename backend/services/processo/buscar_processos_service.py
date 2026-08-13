"""
Caso de uso: busca combinada de processos.

Funcionalidade 03 - Busca por Processo.

Usa o Repository porque a consulta junta cinco tabelas e aceita filtros
opcionais. A busca por id continua na Model, que resolve sozinha.
"""

from repositories.processo_repository import ProcessoRepository


class BuscarProcessosService:
    @staticmethod
    def executar(termo=None, status_id=None, advogado_id=None, tipo_id=None):
        termo = (termo or "").strip() or None

        if termo and len(termo) < 2:
            raise ValueError("Digite ao menos 2 caracteres para buscar.")

        return ProcessoRepository.buscar(
            termo=termo,
            status_id=_inteiro(status_id),
            advogado_id=_inteiro(advogado_id),
            tipo_id=_inteiro(tipo_id),
        )


def _inteiro(valor):
    """Converte para int, devolvendo None quando o filtro não foi usado."""
    if valor in (None, "", "null"):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None
