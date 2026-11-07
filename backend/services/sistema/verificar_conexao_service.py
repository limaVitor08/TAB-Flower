# Confere a conexão com o banco para a rota de status
import logging

from repositories.sistema_repository import SistemaRepository

logger = logging.getLogger("tabflower")


class VerificarConexaoService:
    @staticmethod
    def executar():
        try:
            SistemaRepository.testar_conexao()
        except Exception as erro:
            logger.error("Banco inacessivel: %s", erro)
            raise ConnectionError(str(erro))

        return {"api": "no ar", "banco": "conectado"}
