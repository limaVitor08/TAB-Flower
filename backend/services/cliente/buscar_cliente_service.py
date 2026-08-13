"""
Caso de uso: buscar um cliente específico.
"""

from models.cliente import Cliente
from utils.validador_documento import limpar_documento


class BuscarClienteService:
    """Busca por id ou por documento."""

    @staticmethod
    def por_id(id_cliente):
        cliente = Cliente.buscar_por_id(id_cliente)
        if not cliente:
            raise LookupError("Cliente não encontrado.")
        return cliente

    @staticmethod
    def por_documento(documento):
        """Funcionalidade 02 (Busca por Documento)."""
        documento = limpar_documento(documento)
        if not documento:
            raise ValueError("Informe o documento para a busca.")

        cliente = Cliente.buscar_por_documento(documento)
        if not cliente:
            raise LookupError("Cliente não encontrado.")
        return cliente
