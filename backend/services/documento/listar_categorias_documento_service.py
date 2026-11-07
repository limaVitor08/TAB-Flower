# Lista as categorias de documento para a tela
from models.tabelas_apoio import CategoriaDocumento


class ListarCategoriasDocumentoService:
    @staticmethod
    def executar():
        return CategoriaDocumento.listar_todos()
