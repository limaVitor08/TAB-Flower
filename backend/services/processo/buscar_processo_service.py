"""
Caso de uso: buscar um processo específico.

Funcionalidade 03 (Busca por Processo).
"""

from models.processo import Processo


class BuscarProcessoService:
    @staticmethod
    def por_id(id_processo):
        processo = Processo.buscar_por_id(id_processo)
        if not processo:
            raise LookupError("Processo não encontrado.")
        return processo

    @staticmethod
    def por_numero(numero):
        numero = (numero or "").strip()
        if not numero:
            raise ValueError("Informe o número do processo.")

        processo = Processo.buscar_por_numero(numero)
        if not processo:
            raise LookupError("Processo não encontrado.")
        return processo
