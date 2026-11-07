# Lista todos os documentos, com ou sem os excluídos
from models.documento import Documento


class ListarDocumentosService:
    @staticmethod
    def executar(incluir_excluidos=False):
        return Documento.listar_todos(incluir_excluidos=incluir_excluidos)
