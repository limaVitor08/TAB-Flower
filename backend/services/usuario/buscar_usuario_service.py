# Encontra um usuário pelo id
from models.usuario import Usuario


class BuscarUsuarioService:
    @staticmethod
    def executar(id_usuario):
        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        return usuario
