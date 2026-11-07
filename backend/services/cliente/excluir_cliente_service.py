# Desativa um cliente sem apagar do banco, só o Admin pode
from models.cliente import Cliente
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)
class ExcluirClienteService:
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
        RegistrarAuditoriaService.executar(
            usuario_id=usuario.id,
            acao="EXCLUIR",
            entidade="cliente",
            entidade_id=cliente.id,
            descricao=f"Cliente {cliente.nome} desativado.",
        )
        return cliente.deletar()
