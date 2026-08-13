"""
Caso de uso: buscar um usuário específico.
"""

from models.usuario import Usuario


class BuscarUsuarioService:
    @staticmethod
    def por_id(id_usuario):
        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        return usuario
