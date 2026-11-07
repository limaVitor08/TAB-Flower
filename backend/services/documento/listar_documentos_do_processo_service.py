# Lista os documentos de um processo
from models.documento import Documento


class ListarDocumentosDoProcessoService:
    @staticmethod
    def executar(processo_id, incluir_excluidos=False):
        return Documento.listar_do_processo(processo_id, incluir_excluidos)
