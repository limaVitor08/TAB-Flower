"""
Caso de uso: listar os processos.
"""

from models.processo import Processo


class ListarProcessosService:
    @staticmethod
    def executar(apenas_ativos=True):
        return Processo.listar_todos(apenas_ativos=apenas_ativos)

    @staticmethod
    def do_cliente(cliente_id):
        """Processos de um cliente específico."""
        return Processo.listar_do_cliente(cliente_id)
