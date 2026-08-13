"""
Caso de uso: atualizar os dados de um cliente.
"""

from models.cliente import Cliente


class AtualizarClienteService:
    """Válida os dados enviados e grava a alteração."""

    @staticmethod
    def executar(id_cliente, dados):
        cliente = Cliente.buscar_por_id(id_cliente)
        if not cliente:
            raise LookupError("Cliente não encontrado.")

        # O documento não pode ser alterado: mudar o CPF/CNPJ depois do
        # cadastro contornaria o bloqueio de duplicidade.
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
