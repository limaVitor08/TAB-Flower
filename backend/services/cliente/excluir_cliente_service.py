"""
Caso de uso: excluir (desativar) um cliente.
"""

from models.cliente import Cliente
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)


class ExcluirClienteService:
    """Desativa o cliente sem apagar o histórico.

    Funcionalidade 20 (Restricao de Exclusão): o registro permanece no
    banco para não quebrar os processos e documentos ligados a ele, e
    só quem tem permissão de exclusão (hoje, o perfil Admin) pode
    executar esta ação.
    """

    @staticmethod
    def executar(id_cliente, usuario):
        if not usuario.perfil or not usuario.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario.perfil.nome if usuario.perfil else 'atual'} "
                "não tem permissão para excluir clientes. "
                "Somente o Administrador pode."
            )

        cliente = Cliente.buscar_por_id(id_cliente)
        if not cliente:
            raise LookupError("Cliente não encontrado.")

        if not cliente.ativo:
            raise ValueError("Este cliente já está inativo.")

        # A auditoria e registrada ANTES do remover(). O commit que esta
        # dentro do remover() grava a desativação e o log de uma vez so:
        # não existe cliente desativado sem registro de quem desativou.
        RegistrarAuditoriaService.registrar(
            usuario_id=usuario.id,
            acao="EXCLUIR",
            entidade="cliente",
            entidade_id=cliente.id,
            descricao=f"Cliente {cliente.nome} desativado.",
        )

        return cliente.remover()
