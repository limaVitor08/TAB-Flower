# Encontra um processo pelo id
from models.processo import Processo


class BuscarProcessoService:
    @staticmethod
    def executar(id_processo):
        processo = Processo.buscar_por_id(id_processo)
        if not processo:
            raise LookupError("Processo não encontrado.")
        return processo
