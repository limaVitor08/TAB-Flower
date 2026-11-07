# Avança o processo de fase quando os documentos obrigatórios chegam
from models.checklist import ChecklistProcesso
from models.tabelas_apoio import StatusProcesso
from services.processo.atualizar_status_service import AtualizarStatusService


class AvancarStatusAutomaticoService:
    OBSERVACAO_AVANCO = "Documentação obrigatória completa — avanço automático."

    @staticmethod
    def executar(processo, usuario_id=None):
        if ChecklistProcesso.tem_pendencia_obrigatoria(processo.id):
            return None

        fases = StatusProcesso.listar_todos()
        if len(fases) < 2:
            return None

        primeira, segunda = fases[0], fases[1]

        if processo.status_id != primeira.id:
            return None

        AtualizarStatusService.executar(
            processo.id,
            segunda.id,
            usuario_id,
            AvancarStatusAutomaticoService.OBSERVACAO_AVANCO,
            confirmar=False,
        )

        return segunda
