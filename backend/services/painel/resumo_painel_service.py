"""
Monta o resumo do painel (funcionalidade 6).

Usa o Repository porque a consulta conta os processos de cada fase com
LEFT JOIN.
"""

from repositories.processo_repository import ProcessoRepository


class ResumoPainelService:
    @staticmethod
    def executar():
        linhas = ProcessoRepository.painel_resumo()

        # O total geral e calculado aqui, na camada de aplicação, e não
        # em mais uma ida ao banco.
        total = sum(int(l["total_processos"] or 0) for l in linhas)
        vencidos = sum(int(l["total_vencidos"] or 0) for l in linhas)
        vencendo = sum(int(l["total_vencendo"] or 0) for l in linhas)

        return {
            "por_status": linhas,
            "total_processos": total,
            "total_vencidos": vencidos,
            "total_vencendo": vencendo,
        }
