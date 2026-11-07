# Lista os clientes que entraram numa importação
from models.cliente import Cliente
from models.importacao import ImportacaoLote
class ListarClientesDoLoteService:
    @staticmethod
    def executar(id_importacao):
        lote = ImportacaoLote.buscar_por_id(id_importacao)
        if not lote:
            raise LookupError("Importação não encontrada.")
        return Cliente.query.filter_by(importacao_id=lote.id).order_by(
            Cliente.nome
        ).all()
