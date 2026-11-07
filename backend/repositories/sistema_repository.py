# Confere se o banco está respondendo
from sqlalchemy import text

from extensions import db


class SistemaRepository:

    @staticmethod
    def testar_conexao():
        db.session.execute(text("SELECT 1"))
