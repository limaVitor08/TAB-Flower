# Lista as importações já feitas
from models.importacao import ImportacaoLote
class ListarImportacoesService:
    @staticmethod
    def executar():
        return ImportacaoLote.listar_todos()
