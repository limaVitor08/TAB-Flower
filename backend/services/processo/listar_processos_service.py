# Lista os processos, só os ativos ou também os arquivados
from models.processo import Processo


class ListarProcessosService:
    @staticmethod
    def executar(apenas_ativos=True):
        return Processo.listar_todos(apenas_ativos=apenas_ativos)
