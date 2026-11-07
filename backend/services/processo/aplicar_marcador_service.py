# Aplica um marcador de prioridade a um processo
from extensions import db
from models.processo import Processo
from models.tabelas_apoio import Marcador
from repositories.marcador_repository import MarcadorRepository


class AplicarMarcadorService:
    @staticmethod
    def executar(processo_id, marcador_id, usuario_id=None):
        processo = Processo.buscar_por_id(processo_id)
        if not processo:
            raise LookupError("Processo não encontrado.")

        marcador = db.session.get(Marcador, marcador_id)
        if not marcador:
            raise ValueError("Marcador inválido.")

        if MarcadorRepository.esta_aplicado(processo_id, marcador_id):
            raise ValueError("Este marcador já foi aplicado ao processo.")

        MarcadorRepository.aplicar(processo_id, marcador_id, usuario_id)
        db.session.commit()

        return MarcadorRepository.listar_do_processo(processo_id)
