"""Busca um documento pelo id."""

from models.documento import Documento


class BuscarDocumentoService:
    @staticmethod
    def por_id(id_documento):
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")
        return documento
