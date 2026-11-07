# Model do lote de importação, com quantas linhas entraram e quantas falharam
from datetime import datetime
from extensions import db
class ImportacaoLote(db.Model):
    __tablename__ = "importacao_lote"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    nome_arquivo = db.Column(db.String(200), nullable=False)
    total_registros = db.Column(db.Integer, nullable=False, default=0)
    total_sucesso = db.Column(db.Integer, nullable=False, default=0)
    total_erro = db.Column(db.Integer, nullable=False, default=0)
    situacao = db.Column(
        db.Enum("PROCESSANDO", "CONCLUIDA", "FALHOU"),
        nullable=False,
        default="PROCESSANDO",
    )
    log_erros = db.Column(db.Text)
    criado_em = db.Column(db.DateTime)
    finalizado_em = db.Column(db.DateTime)
    usuario = db.relationship("Usuario", lazy="joined")
    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self
    def finalizar(self, situacao, total_sucesso, total_erro, log_erros):
        self.situacao = situacao
        self.total_sucesso = total_sucesso
        self.total_erro = total_erro
        self.log_erros = log_erros
        self.finalizado_em = datetime.now()
        db.session.commit()
        return self
    @staticmethod
    def buscar_por_id(id_importacao):
        return db.session.get(ImportacaoLote, id_importacao)
    @staticmethod
    def listar_todos():
        return ImportacaoLote.query.order_by(ImportacaoLote.criado_em.desc()).all()
    def to_dict(self):
        return {
            "id": self.id,
            "nome_arquivo": self.nome_arquivo,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "total_registros": self.total_registros,
            "total_sucesso": self.total_sucesso,
            "total_erro": self.total_erro,
            "situacao": self.situacao,
            "log_erros": self.log_erros,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "finalizado_em": (
                self.finalizado_em.isoformat() if self.finalizado_em else None
            ),
            }
