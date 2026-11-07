# Lista as mudanças de fase de um processo
from models.processo import HistoricoStatus


class ListarHistoricoService:
    @staticmethod
    def executar(processo_id):
        return HistoricoStatus.listar_do_processo(processo_id)
