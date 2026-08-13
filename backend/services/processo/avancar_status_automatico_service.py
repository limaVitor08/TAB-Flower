"""
Caso de uso: avançar a situação do processo quando a documentação fica
completa.

Funcionalidade 07 (Atualização de Status), em conjunto com a 11 e a 12.

Por que este avanço é automático e os outros não: o sistema só pode
decidir sozinho o que ele mesmo consegue verificar. "A documentação está
completa" é uma informação que vive inteira dentro do banco, então dá
para concluir sem perguntar a ninguém. Já "foi protocolado no fórum"
depende do mundo lá fora, e nenhuma automação adivinharia isso.

A regra é deliberadamente estreita: o avanço só acontece quando o
processo está na PRIMEIRA fase configurada, que é justamente a fase que
o checklist governa. Um processo em andamento não muda de situação
sozinho porque alguém anexou um documento.
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

        Nada é confirmado aqui: este avanço é consequência do anexo, e quem
        grava tudo de uma vez é o EnviarDocumentoService.
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

        A contrapartida do avanço: se o processo tinha subido de fase por
        estar completo e voltou a ter pendência, ele desce de volta. Sem
        isso, um processo apareceria como "Pronto para protocolo" com
        documento faltando.
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
        """Ainda falta algum documento OBRIGATÓRIO?

        Itens opcionais não seguram o processo: eles existem no checklist
        para lembrar a secretária, não para bloquear o andamento.
        """
        pendente = ChecklistProcesso.query.filter_by(
            processo_id=processo_id,
            obrigatorio=True,
            entregue=False,
        ).first()

        return pendente is not None
