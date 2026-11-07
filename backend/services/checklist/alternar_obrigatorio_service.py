# Troca um item do molde entre obrigatório e opcional
from extensions import db
from models.checklist import ChecklistModelo
from services.checklist.listar_itens_modelo_service import ListarItensModeloService


class AlternarObrigatorioService:
    @staticmethod
    def executar(id_item):
        item = db.session.get(ChecklistModelo, id_item)
        if not item:
            raise LookupError("Item de checklist não encontrado.")

        item.obrigatorio = not item.obrigatorio
        db.session.commit()

        return ListarItensModeloService.executar(item.tipo_processo_id)
