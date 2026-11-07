# Edita os dados de um cliente, sem permitir desativar por aqui
from models.cliente import Cliente


class AtualizarClienteService:
    @staticmethod
    def executar(id_cliente, dados, usuario_logado):
        cliente = Cliente.buscar_por_id(id_cliente)
        if not cliente:
            raise LookupError("Cliente não encontrado.")

        if "ativo" in dados:
            if not usuario_logado.perfil or not usuario_logado.perfil.pode_excluir:
                raise PermissionError(
                    "Só o Administrador desativa clientes, e pelo botão Desativar."
                )
            raise ValueError("Para desativar o cliente, use o botão Desativar.")

        if "documento" in dados:
            documento_novo = str(dados["documento"]).strip()
            if documento_novo and documento_novo != cliente.documento:
                raise ValueError(
                    "O documento do cliente não pode ser alterado. "
                    "Cadastre um novo cliente se necessário."
                )

        if "nome" in dados and not (dados["nome"] or "").strip():
            raise ValueError("O nome do cliente é obrigatório.")

        return cliente.atualizar(dados)
