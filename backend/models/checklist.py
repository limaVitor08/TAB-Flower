"""
Models do checklist de documentos.

O checklist_modelo é o molde. O que cada tipo de processo exige. O
checklist_processo é a cópia que vai para cada processo aberto.
Separamos os dois para que mudar o molde hoje não mexa no checklist de
um processo aberto no mês passado.
"""

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
        """Itens exigidos por um tipo de processo. Funcionalidade 13."""
        return (
            ChecklistModelo.query.filter_by(tipo_processo_id=tipo_processo_id)
            .order_by(ChecklistModelo.ordem)
            .all()
        )


class ChecklistProcesso(db.Model):
    """Um item do checklist de um processo.

    Funcionalidade 11 (Checklist Obrigatório) e 12 (Mapeamento de
    Pendências). Itens com entregue = False são as pendências.
    """

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

    def to_dict(self):
        return {
            "id": self.id,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria.nome if self.categoria else None,
            "obrigatorio": self.obrigatorio,
            "entregue": self.entregue,
        }
