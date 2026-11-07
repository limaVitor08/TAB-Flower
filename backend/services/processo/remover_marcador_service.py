# Tira um marcador de um processo
from extensions import db
from repositories.marcador_repository import MarcadorRepository


class RemoverMarcadorService:
    @staticmethod
    def executar(processo_id, marcador_id):
        removidos = MarcadorRepository.remover(processo_id, marcador_id)
        db.session.commit()

        if removidos == 0:
            raise LookupError("Este marcador não estava aplicado ao processo.")

        return MarcadorRepository.listar_do_processo(processo_id)
