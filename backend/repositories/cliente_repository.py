# Busca clientes pelo nome usando uma stored procedure
from sqlalchemy import text
from extensions import db
from utils.conversao import converter_linhas
class ClienteRepository:
    @staticmethod
    def buscar_por_nome(termo, apenas_ativos=True):
        resultado = db.session.execute(
            text("CALL sp_buscar_clientes_por_nome(:termo, :apenas_ativos)"),
            {"termo": termo, "apenas_ativos": apenas_ativos},
        )
        return converter_linhas(resultado)
