# Encontra um cliente pelo CPF ou CNPJ completo
from models.cliente import Cliente
from utils.validador_documento import limpar_documento
class BuscarClientePorDocumentoService:
    @staticmethod
    def executar(documento):
        documento = limpar_documento(documento)
        if not documento:
            raise ValueError("Informe o documento para a busca.")
        cliente = Cliente.buscar_por_documento(documento)
        if not cliente:
            raise LookupError("Cliente não encontrado.")
        return cliente
