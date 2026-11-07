# Marca um aviso como lido, só pelo próprio destinatário
from models.notificacao import Notificacao


class MarcarNotificacaoLidaService:
    @staticmethod
    def executar(id_notificacao, usuario):
        aviso = Notificacao.buscar_por_id(id_notificacao)
        if not aviso:
            raise LookupError("Notificação não encontrada.")

        if aviso.usuario_destino_id != usuario.id:
            raise PermissionError("Este aviso não é seu.")

        return aviso.marcar_lida()
