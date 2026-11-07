# Model dos avisos que o advogado recebe quando chega documento
from datetime import datetime

from extensions import db


class Notificacao(db.Model):
    __tablename__ = "notificacao"

    id = db.Column(db.Integer, primary_key=True)
    usuario_destino_id = db.Column(
        db.Integer, db.ForeignKey("usuario.id"), nullable=False
    )
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"))
    documento_id = db.Column(db.Integer, db.ForeignKey("documento.id"))
    titulo = db.Column(db.String(120), nullable=False)
    mensagem = db.Column(db.String(255), nullable=False)
    tipo = db.Column(
        db.Enum("DOCUMENTO", "PRAZO", "STATUS", "GERAL"),
        nullable=False,
        default="GERAL",
    )
    lida = db.Column(db.Boolean, nullable=False, default=False)
    lida_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime)

    def salvar(self, confirmar=False):
        db.session.add(self)
        if confirmar:
            db.session.commit()
        return self

    def marcar_lida(self):
        self.lida = True
        self.lida_em = datetime.now()
        db.session.commit()
        return self

    @staticmethod
    def buscar_por_id(id_notificacao):
        return db.session.get(Notificacao, id_notificacao)

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_destino_id": self.usuario_destino_id,
            "processo_id": self.processo_id,
            "documento_id": self.documento_id,
            "titulo": self.titulo,
            "mensagem": self.mensagem,
            "tipo": self.tipo,
            "lida": self.lida,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
