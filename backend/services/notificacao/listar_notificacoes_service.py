# Lista os avisos de quem está logado
from repositories.notificacao_repository import NotificacaoRepository


class ListarNotificacoesService:
    @staticmethod
    def executar(usuario_id, apenas_nao_lidas=False):
        return NotificacaoRepository.do_advogado(usuario_id, apenas_nao_lidas)
