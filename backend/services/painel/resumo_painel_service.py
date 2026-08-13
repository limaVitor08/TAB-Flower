"""
Caso de uso: montar o painel central de gestao.

Funcionalidade 06 - Painel Central de Gestao.

Este Service usa o Repository, e não a Model, porque a consulta e uma
agregação com LEFT JOIN - relatório, não CRUD.
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
