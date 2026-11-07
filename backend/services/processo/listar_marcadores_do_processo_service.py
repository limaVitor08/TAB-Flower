# Lista os marcadores aplicados a um processo
from repositories.marcador_repository import MarcadorRepository


class ListarMarcadoresDoProcessoService:
    @staticmethod
    def executar(processo_id):
        return MarcadorRepository.listar_do_processo(processo_id)
