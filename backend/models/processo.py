# Models do processo e do histórico de mudanças de fase
from extensions import db


class HistoricoStatus(db.Model):
    __tablename__ = "historico_status"

    id = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"), nullable=False)
    status_anterior_id = db.Column(db.Integer, db.ForeignKey("status_processo.id"))
    status_novo_id = db.Column(
        db.Integer, db.ForeignKey("status_processo.id"), nullable=False
    )
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    observacao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime)

    status_novo = db.relationship("StatusProcesso", foreign_keys=[status_novo_id])
    status_anterior = db.relationship(
        "StatusProcesso", foreign_keys=[status_anterior_id]
    )

    def salvar(self, confirmar=True):
        db.session.add(self)
        if confirmar:
            db.session.commit()
        return self

    @staticmethod
    def listar_do_processo(processo_id):
        return (
            HistoricoStatus.query.filter_by(processo_id=processo_id)
            .order_by(HistoricoStatus.criado_em.desc())
            .all()
        )

    def to_dict(self):
        return {
            "id": self.id,
            "status_anterior": self.status_anterior.nome if self.status_anterior else None,
            "status_novo": self.status_novo.nome if self.status_novo else None,
            "observacao": self.observacao,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }


class Processo(db.Model):
    __tablename__ = "processo"

    id = db.Column(db.Integer, primary_key=True)
    numero_processo = db.Column(db.String(30), nullable=False, unique=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    advogado_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    tipo_processo_id = db.Column(
        db.Integer, db.ForeignKey("tipo_processo.id"), nullable=False
    )
    status_id = db.Column(
        db.Integer, db.ForeignKey("status_processo.id"), nullable=False
    )
    comarca = db.Column(db.String(100))
    valor_causa = db.Column(db.Numeric(12, 2))
    data_abertura = db.Column(db.Date, nullable=False)
    prazo_final = db.Column(db.Date)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    importacao_id = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime)
    atualizado_em = db.Column(db.DateTime)

    cliente = db.relationship("Cliente", lazy="joined")
    advogado = db.relationship("Usuario", lazy="joined")
    tipo = db.relationship("TipoProcesso", lazy="joined")
    status = db.relationship("StatusProcesso", lazy="joined")


    def salvar(self, confirmar=True):
        db.session.add(self)
        if confirmar:
            db.session.commit()
        else:
            db.session.flush()
        return self

    def atualizar(self, dados):
        campos_editaveis = [
            "titulo",
            "descricao",
            "advogado_id",
            "comarca",
            "valor_causa",
            "prazo_final",
        ]

        for campo in campos_editaveis:
            if campo in dados:
                setattr(self, campo, dados[campo])

        db.session.commit()
        return self

    def deletar(self):
        self.ativo = False
        db.session.commit()
        return self


    @staticmethod
    def buscar_por_id(id_processo):
        return db.session.get(Processo, id_processo)

    @staticmethod
    def buscar_por_numero(numero):
        return Processo.query.filter_by(numero_processo=numero).first()

    @staticmethod
    def listar_todos(apenas_ativos=True):
        consulta = Processo.query
        if apenas_ativos:
            consulta = consulta.filter_by(ativo=True)
        return consulta.order_by(Processo.data_abertura.desc()).all()


    def to_dict(self):
        return {
            "id": self.id,
            "numero_processo": self.numero_processo,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "cliente_id": self.cliente_id,
            "cliente_nome": self.cliente.nome if self.cliente else None,
            "advogado_id": self.advogado_id,
            "advogado_nome": self.advogado.nome if self.advogado else None,
            "tipo_processo_id": self.tipo_processo_id,
            "tipo_nome": self.tipo.nome if self.tipo else None,
            "status_id": self.status_id,
            "status_nome": self.status.nome if self.status else None,
            "status_cor": self.status.cor_hex if self.status else None,
            "comarca": self.comarca,
            "valor_causa": float(self.valor_causa) if self.valor_causa is not None else None,
            "data_abertura": self.data_abertura.isoformat() if self.data_abertura else None,
            "prazo_final": self.prazo_final.isoformat() if self.prazo_final else None,
            "ativo": self.ativo,
        }

    def __repr__(self):
        return f"<Processo {self.id} - {self.numero_processo}>"
