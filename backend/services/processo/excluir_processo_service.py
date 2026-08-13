"""
Caso de uso: arquivar (desativar) um processo.

Funcionalidade 20 (Restricao de Exclusão).
"""

from models.processo import Processo
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)


class ExcluirProcessoService:
    @staticmethod
    def executar(id_processo, usuario):
        if not usuario.perfil or not usuario.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario.perfil.nome if usuario.perfil else 'atual'} "
                "não tem permissão para arquivar processos. "
                "Somente o Administrador pode."
            )

        processo = Processo.buscar_por_id(id_processo)
        if not processo:
            raise LookupError("Processo não encontrado.")

        if not processo.ativo:
            raise ValueError("Este processo já está arquivado.")

        # Registrada antes do remover(): o commit do remover() grava o
        # arquivamento e o log na mesma transação.
        RegistrarAuditoriaService.registrar(
            usuario_id=usuario.id,
            acao="EXCLUIR",
            entidade="processo",
            entidade_id=processo.id,
            descricao=f"Processo {processo.numero_processo} arquivado.",
        )

        return processo.remover()
