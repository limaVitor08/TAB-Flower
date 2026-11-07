# Lista o checklist de documentos de um processo
from models.checklist import ChecklistProcesso


class ListarChecklistDoProcessoService:
    @staticmethod
    def executar(processo_id):
        return ChecklistProcesso.listar_do_processo(processo_id)
