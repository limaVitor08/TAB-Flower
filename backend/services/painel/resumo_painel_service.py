# Conta os processos de cada fase para o painel
from repositories.processo_repository import ProcessoRepository


class ResumoPainelService:
    @staticmethod
    def executar():
        linhas = ProcessoRepository.painel_resumo()

        total = sum(int(l["total_processos"] or 0) for l in linhas)
        vencidos = sum(int(l["total_vencidos"] or 0) for l in linhas)
        vencendo = sum(int(l["total_vencendo"] or 0) for l in linhas)

        return {
            "por_status": linhas,
            "total_processos": total,
            "total_vencidos": vencidos,
            "total_vencendo": vencendo,
        }
