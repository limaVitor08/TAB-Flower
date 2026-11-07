# Volta o processo para a primeira fase quando uma pendência reabre
from models.checklist import ChecklistProcesso
from models.tabelas_apoio import StatusProcesso
from services.processo.atualizar_status_service import AtualizarStatusService


class RetrocederStatusAutomaticoService:
    OBSERVACAO_RETORNO = "Documento removido — pendência reaberta."

    @staticmethod
    def executar(processo, usuario_id=None):
        if not ChecklistProcesso.tem_pendencia_obrigatoria(processo.id):
            return None

        fases = StatusProcesso.listar_todos()
        if len(fases) < 2:
            return None

        primeira, segunda = fases[0], fases[1]

        if processo.status_id != segunda.id:
            return None

        AtualizarStatusService.executar(
            processo.id,
            primeira.id,
            usuario_id,
            RetrocederStatusAutomaticoService.OBSERVACAO_RETORNO,
            confirmar=False,
        )

        return primeira
