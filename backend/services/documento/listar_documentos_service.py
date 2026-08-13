"""
Caso de uso: listar documentos.
"""

from models.documento import Documento


class ListarDocumentosService:
    @staticmethod
    def executar(incluir_excluidos=False):
        return Documento.listar_todos(incluir_excluidos=incluir_excluidos)

    @staticmethod
    def do_processo(processo_id, incluir_excluidos=False):
        return Documento.listar_do_processo(processo_id, incluir_excluidos)

    @staticmethod
    def do_cliente(cliente_id, incluir_excluidos=False):
        return Documento.listar_do_cliente(cliente_id, incluir_excluidos)
