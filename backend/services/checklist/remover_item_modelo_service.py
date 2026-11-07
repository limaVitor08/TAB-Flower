# Tira um documento exigido do molde do checklist
from extensions import db
from models.checklist import ChecklistModelo
from services.checklist.listar_itens_modelo_service import ListarItensModeloService


class RemoverItemModeloService:
    @staticmethod
    def executar(id_item):
        item = db.session.get(ChecklistModelo, id_item)
        if not item:
            raise LookupError("Item de checklist não encontrado.")

        tipo_id = item.tipo_processo_id
        db.session.delete(item)
        db.session.commit()

        return ListarItensModeloService.executar(tipo_id)
