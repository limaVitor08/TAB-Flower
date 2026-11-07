# Model do log de auditoria, que guarda quem fez cada ação registrada e quando
from extensions import db
class LogAuditoria(db.Model):
    __tablename__ = "log_auditoria"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    acao = db.Column(
        db.Enum("CRIAR", "ATUALIZAR", "EXCLUIR", "RESTAURAR", "LOGIN", "DOWNLOAD"),
        nullable=False,
    )
    entidade = db.Column(db.String(50), nullable=False)
    entidade_id = db.Column(db.Integer)
    descricao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime)
    usuario = db.relationship("Usuario", lazy="joined")
    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "acao": self.acao,
            "entidade": self.entidade,
            "entidade_id": self.entidade_id,
            "descricao": self.descricao,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
    def __repr__(self):
        return f"<LogAuditoria {self.id} - {self.acao} em {self.entidade}>"
