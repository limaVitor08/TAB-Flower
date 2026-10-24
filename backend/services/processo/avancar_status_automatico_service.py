"""
Avança o processo de fase quando a documentação fica completa.

O sistema só decide sozinho o que ele consegue conferir no banco. Saber
se todos os documentos obrigatórios chegaram dá para conferir. Saber se
o processo já foi protocolado no fórum, não. Por isso o avanço é só da
primeira fase para a segunda, que é a fase controlada pelo checklist. Um
processo em andamento não muda de fase porque alguém anexou um arquivo.
"""

from models.checklist import ChecklistProcesso
from models.tabelas_apoio import StatusProcesso
from services.processo.atualizar_status_service import AtualizarStatusService


class AvancarStatusAutomaticoService:
    """Move o processo de fase quando o checklist obrigatório é cumprido."""

    OBSERVACAO_AVANCO = "Documentação obrigatória completa — avanço automático."
    OBSERVACAO_RETORNO = "Documento removido — pendência reaberta."

    @staticmethod
    def ao_completar_checklist(processo, usuario_id=None):
        """Chamado depois que um documento é anexado.

        Devolve o novo status se houve avanço, ou None se nada mudou.
        """
        if AvancarStatusAutomaticoService._tem_pendencia(processo.id):
            return None

        fases = StatusProcesso.listar_todos()
        if len(fases) < 2:
            return None

        primeira, segunda = fases[0], fases[1]

        # Só avança quem está parado esperando documento.
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

    @staticmethod
    def ao_reabrir_pendencia(processo, usuario_id=None):
        """Chamado depois que um documento é excluído.
        """
        if not AvancarStatusAutomaticoService._tem_pendencia(processo.id):
            return None

        fases = StatusProcesso.listar_todos()
        if len(fases) < 2:
            return None

        primeira, segunda = fases[0], fases[1]

        # Só volta quem tinha avançado. Um processo já protocolado não
        # regride por causa de um documento removido do acervo.
        if processo.status_id != segunda.id:
            return None

        AtualizarStatusService.executar(
            processo.id,
            primeira.id,
            usuario_id,
            AvancarStatusAutomaticoService.OBSERVACAO_RETORNO,
            confirmar=False,
        )

        return primeira

    @staticmethod
    def _tem_pendencia(processo_id):
        """
        Itens opcionais não seguram o processo,eles existem no checklist
        para lembrar a secretária, não para bloquear o andamento.
        """
        pendente = ChecklistProcesso.query.filter_by(
            processo_id=processo_id,
            obrigatorio=True,
            entregue=False,
        ).first()

        return pendente is not None
