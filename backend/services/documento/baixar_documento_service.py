# Prepara o download de um documento que não foi excluído
import os

from config import Config
from models.documento import Documento


class BaixarDocumentoService:
    @staticmethod
    def executar(id_documento):
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")

        if documento.excluido:
            raise LookupError("Este documento foi excluído.")

        caminho = os.path.join(Config.PASTA_ARQUIVOS, documento.caminho_arquivo)
        if not os.path.exists(caminho):
            raise LookupError("O arquivo não foi encontrado no servidor.")

        return {
            "pasta": os.path.dirname(caminho),
            "arquivo": os.path.basename(caminho),
            "nome_download": documento.nome_padronizado,
        }
