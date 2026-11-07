# Models do molde do checklist e da cópia que cada processo recebe
from extensions import db


class ChecklistModelo(db.Model):
    __tablename__ = "checklist_modelo"

    id = db.Column(db.Integer, primary_key=True)
    tipo_processo_id = db.Column(
        db.Integer, db.ForeignKey("tipo_processo.id"), nullable=False
    )
    categoria_id = db.Column(
        db.Integer, db.ForeignKey("categoria_documento.id"), nullable=False
    )
    obrigatorio = db.Column(db.Boolean, nullable=False, default=True)
    ordem = db.Column(db.Integer, default=0)

    @staticmethod
    def listar_do_tipo(tipo_processo_id):
        return (
            ChecklistModelo.query.filter_by(tipo_processo_id=tipo_processo_id)
            .order_by(ChecklistModelo.ordem)
            .all()
        )


class ChecklistProcesso(db.Model):
    __tablename__ = "checklist_processo"

    id = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"), nullable=False)
    categoria_id = db.Column(
        db.Integer, db.ForeignKey("categoria_documento.id"), nullable=False
    )
    documento_id = db.Column(db.Integer, db.ForeignKey("documento.id"))
    obrigatorio = db.Column(db.Boolean, nullable=False, default=True)
    entregue = db.Column(db.Boolean, nullable=False, default=False)
    entregue_em = db.Column(db.DateTime)
    observacao = db.Column(db.String(200))

    categoria = db.relationship("CategoriaDocumento", lazy="joined")

    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def listar_do_processo(processo_id):
        return (
            ChecklistProcesso.query.filter_by(processo_id=processo_id)
            .order_by(ChecklistProcesso.id)
            .all()
        )

    @staticmethod
    def tem_pendencia_obrigatoria(processo_id):
        pendente = ChecklistProcesso.query.filter_by(
            processo_id=processo_id,
            obrigatorio=True,
            entregue=False,
        ).first()

        return pendente is not None

    def to_dict(self):
        return {
            "id": self.id,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria.nome if self.categoria else None,
            "obrigatorio": self.obrigatorio,
            "entregue": self.entregue,
        }
