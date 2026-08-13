"""
Caso de uso: listar os clientes cadastrados.
"""

from models.cliente import Cliente


class ListarClientesService:
    """Devolve a lista de clientes em ordem alfabetica."""

    @staticmethod
    def executar(apenas_ativos=True):
        return Cliente.listar_todos(apenas_ativos=apenas_ativos)
