"""Lista as importações feitas e os clientes de cada uma (funcionalidade 19)."""
from models.cliente import Cliente
from models.importacao import ImportacaoLote
class ListarImportacoesService:
    @staticmethod
    def executar():
        return ImportacaoLote.listar_todas()
    @staticmethod
    def clientes_do_lote(id_importacao):
        """Quais clientes entraram nesta carga."""
        lote = ImportacaoLote.buscar_por_id(id_importacao)
        if not lote:
            raise LookupError("Importação não encontrada.")
        return Cliente.query.filter_by(importacao_id=lote.id).order_by(
            Cliente.nome
        ).all()