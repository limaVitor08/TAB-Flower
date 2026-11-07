# Lista os clientes em ordem alfabética
from models.cliente import Cliente
class ListarClientesService:
    @staticmethod
    def executar(apenas_ativos=True):
        return Cliente.listar_todos(apenas_ativos=apenas_ativos)
