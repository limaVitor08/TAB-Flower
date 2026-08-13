"""
Caso de uso: buscar clientes pelo nome.

Funcionalidade 01 (Busca por Nome).

Este Service usa o Repository, e não a Model, porque a consulta envolve
LIKE com filtro parcial e um LEFT JOIN que conta os processos ativos de
cada cliente - relatório, não CRUD.

Como a procedure devolve linhas cruas do banco, e não objetos Cliente,
os campos derivados que a tela espera são montados aqui, na camada de
aplicação. A Model faria isso no to_dict(), mas ela não participa desta
consulta.
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
