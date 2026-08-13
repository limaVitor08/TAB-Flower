"""
Repository do Cliente.

Camada de Persistência Especializada.

Aqui ficam as consultas que extrapolam o CRUD. Nesta etapa elas deixaram
de ser montadas pelo SQLAlchemy e passaram a chamar stored procedures do
MySQL, com a lógica de consulta vivendo no banco.

O CRUD simples continua na Model. Se a operação e apenas salvar, buscar
por id ou listar tudo, ela Não passa por este arquivo.
"""

from sqlalchemy import text

from extensions import db
from utils.conversao import converter_linhas


class ClienteRepository:
    """Consultas específicas do domínio Cliente."""

    @staticmethod
    def buscar_por_nome(termo, apenas_ativos=True):
        """Funcionalidade 01 - Busca por Nome.

        Chama sp_buscar_clientes_por_nome, que faz a busca parcial e ainda
        traz a contagem de processos ativos de cada cliente - informação
        que exige um LEFT JOIN com agregação.
        """
        resultado = db.session.execute(
            text("CALL sp_buscar_clientes_por_nome(:termo, :apenas_ativos)"),
            {"termo": termo, "apenas_ativos": apenas_ativos},
        )

        # A procedure devolve linhas, não objetos Cliente. Convertemos em
        # dicionarios porque a tela precisa de campos que a Model não tem
        # (o total_processos vem do JOIN, não da tabela cliente).
        return converter_linhas(resultado)
