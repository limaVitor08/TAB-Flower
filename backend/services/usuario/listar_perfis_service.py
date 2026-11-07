# Lista os perfis de acesso para a tela de usuários
from models.usuario import Perfil


class ListarPerfisService:
    @staticmethod
    def executar():
        return Perfil.listar_todos()
