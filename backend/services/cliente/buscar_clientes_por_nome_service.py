# Busca clientes por parte do nome
from repositories.cliente_repository import ClienteRepository
from utils.validador_documento import formatar_documento
class BuscarClientesPorNomeService:
    @staticmethod
    def executar(termo, apenas_ativos=True):
        termo = (termo or "").strip()
        if not termo:
            raise ValueError("Informe um nome para a busca.")
        if len(termo) < 2:
            raise ValueError("Digite ao menos 2 caracteres para buscar.")
        linhas = ClienteRepository.buscar_por_nome(termo, apenas_ativos)
        for linha in linhas:
            linha["documento_formatado"] = formatar_documento(
                linha.get("documento"), linha.get("tipo_pessoa")
            )
            linha["total_processos"] = int(linha.get("total_processos") or 0)
        return linhas
