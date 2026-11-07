# Encontra um cliente pelo id
from models.cliente import Cliente
class BuscarClienteService:
    @staticmethod
    def executar(id_cliente):
        cliente = Cliente.buscar_por_id(id_cliente)
        if not cliente:
            raise LookupError("Cliente não encontrado.")
        return cliente
