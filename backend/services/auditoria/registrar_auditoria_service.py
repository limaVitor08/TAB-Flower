# Grava uma ação no log de auditoria
from datetime import datetime
from extensions import db
from models.auditoria import LogAuditoria
class RegistrarAuditoriaService:
    @staticmethod
    def executar(usuario_id, acao, entidade, entidade_id=None, descricao=None):
        registro = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            descricao=(descricao or "")[:255] or None,
            criado_em=datetime.now(),
        )
        db.session.add(registro)
        return registro
