"""
Busca clientes pelo nome (funcionalidade 1).
Usamos o Repository e não a Model porque a busca é por pedaço do nome e
ainda conta quantos processos ativos cada cliente tem, com um LEFT JOIN.
Como a procedure devolve linhas cruas, e não objetos Cliente, os campos
que a tela espera, como o documento formatado, são montados aqui.
"""
from repositories.cliente_repository import ClienteRepository
from utils.validador_documento import formatar_documento
class BuscarClientesPorNomeService:
    """Válida o termo, delega ao Repository e completa os campos da tela."""
    @staticmethod
    def executar(termo):
        termo = (termo or "").strip()
        if not termo:
            raise ValueError("Informe um nome para a busca.")
        if len(termo) < 2:
            raise ValueError("Digite ao menos 2 caracteres para buscar.")
        linhas = ClienteRepository.buscar_por_nome(termo)
        # A procedure devolve o documento sem pontuação, como esta gravado
        # no banco. A tela mostra pontuado.
        for linha in linhas:
            linha["documento_formatado"] = formatar_documento(
                linha.get("documento"), linha.get("tipo_pessoa")
            )
            # A contagem vem do JOIN e chega como int do MySQL.
            linha["total_processos"] = int(linha.get("total_processos") or 0)
        return linhas