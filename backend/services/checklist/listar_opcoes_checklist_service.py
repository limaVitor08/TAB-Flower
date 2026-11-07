# Junta os tipos de processo e as categorias para a tela de checklists
from models.tabelas_apoio import CategoriaDocumento, TipoProcesso


class ListarOpcoesChecklistService:
    @staticmethod
    def executar():
        return {
            "tipos": TipoProcesso.listar_todos(),
            "categorias": CategoriaDocumento.listar_todos(),
        }
