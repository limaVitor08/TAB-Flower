"""
Caso de uso: corrigir a categoria de um documento.

Funcionalidade 09. Se a secretaria classificou errado no envio, a
correção acontece aqui - sem mexer no arquivo que já esta no disco.
"""

from extensions import db
from models.documento import Documento
from models.tabelas_apoio import CategoriaDocumento


class AtualizarDocumentoService:
    @staticmethod
    def executar(id_documento, dados):
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")

        if documento.excluido:
            raise ValueError("Não é possível alterar um documento excluído.")

        if "categoria_id" in dados:
            categoria = db.session.get(CategoriaDocumento, dados["categoria_id"])
            if not categoria:
                raise ValueError("Categoria de documento inválida.")

        return documento.atualizar(dados)
