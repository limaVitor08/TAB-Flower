"""
Registra uma ação importante no log de auditoria.
Quem chama este Service é o caso de uso, porque é ele que sabe que
aquilo foi, por exemplo, a exclusão de um cliente.
Se o log tivesse um commit próprio, poderia existir exclusão sem
registro, ou registro de uma exclusão que não aconteceu.
"""
from datetime import datetime
from extensions import db
from models.auditoria import LogAuditoria
class RegistrarAuditoriaService:
    """Prepara o registro de auditoria. O commit é de quem chama."""
    @staticmethod
    def registrar(usuario_id, acao, entidade, entidade_id=None, descricao=None):
        """Coloca uma linha de auditoria na sessão, sem gravar ainda.
        usuario_id  quem fez (vem sempre de g.usuario_atual, nunca da requisição)
        acao        CRIAR, ATUALIZAR, EXCLUIR, RESTAURAR, LOGIN ou DOWNLOAD
        entidade    nome da tabela afetada ("cliente", "processo", ...)
        entidade_id id da linha afetada
        descricao   texto curto para quem for ler o log depois
        """
        registro = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            # O banco corta em 255. Cortar aqui evita que um nome de cliente
            # muito longo derrube a operação inteira por causa do log.
            descricao=(descricao or "")[:255] or None,
            criado_em=datetime.now(),
        )
        db.session.add(registro)
        return registro