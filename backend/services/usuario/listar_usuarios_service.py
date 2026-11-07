# Lista os usuários do sistema
from models.usuario import Usuario


class ListarUsuariosService:
    @staticmethod
    def executar(apenas_ativos=True):
        return Usuario.listar_todos(apenas_ativos=apenas_ativos)
