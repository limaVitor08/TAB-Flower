# Lista os marcadores para o filtro do painel
from models.tabelas_apoio import Marcador


class ListarMarcadoresService:
    @staticmethod
    def executar():
        return Marcador.listar_todos()
