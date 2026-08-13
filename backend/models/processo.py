"""
Model Processo.

Camada de Domínio / Persistência Simples.

Representa a ação judicial. E a entidade central do sistema: liga o
cliente ao advogado responsavel, carrega o status e reune os documentos,
o checklist e os marcadores de prioridade.
"""

from extensions import db


class HistoricoStatus(db.Model):
    """Registro de cada mudanca de fase do processo.

    Funcionalidade 07 (Atualizacao de Status). Guardar o histórico e o que
    permite responder "ha quanto tempo este processo esta parado nesta
    fase", coisa que a planilha do escritório nunca conseguiu dizer.
    """

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
        """Grava o registro de mudanca de fase.

        confirmar=False quando a mudanca de status faz parte de uma
        operação maior (anexar ou excluir documento): ai o commit e do
        Service, para o status e o histórico entrarem juntos.
        """
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

    # Relacoes usadas apenas para exibir nomes na tela.
    # Consultas com filtro e JOIN explicito ficam no Repository.
    cliente = db.relationship("Cliente", lazy="joined")
    advogado = db.relationship("Usuario", lazy="joined")
    tipo = db.relationship("TipoProcesso", lazy="joined")
    status = db.relationship("StatusProcesso", lazy="joined")

    # -----------------------------------------------------------------
    # CRUD básico
    # -----------------------------------------------------------------

    def salvar(self, confirmar=True):
        """Insere o processo no banco.

        confirmar=False quando o processo faz parte de uma operação maior:
        abrir um processo grava também o checklist e a primeira linha do
        histórico, e as três coisas precisam entrar juntas.
        """
        db.session.add(self)
        if confirmar:
            db.session.commit()
        else:
            # flush gera o id, que o checklist e o histórico precisam,
            # sem fechar a transação.
            db.session.flush()
        return self

    def atualizar(self, dados):
        """Altera os campos permitidos.

        O número do processo fica de fora: ele identifica a ação no
        tribunal e trocar geraria um registro paralelo do mesmo caso.
        O status também fica de fora, porque tem caso de uso próprio
        (AtualizarStatusService), que grava o histórico.
        """
        campos_editaveis = [
            "titulo",
            "descricao",
            "advogado_id",
            "comarca",
            "valor_causa",
            "prazo_final",
            "ativo",
        ]

        for campo in campos_editaveis:
            if campo in dados:
                setattr(self, campo, dados[campo])

        db.session.commit()
        return self

    def remover(self):
        """Arquiva o processo (exclusão lógica).

        Funcionalidade 20: documentos e histórico continuam vinculados.
        """
        self.ativo = False
        db.session.commit()
        return self

    # -----------------------------------------------------------------
    # Consultas simples
    # -----------------------------------------------------------------

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

    @staticmethod
    def listar_do_cliente(cliente_id):
        return (
            Processo.query.filter_by(cliente_id=cliente_id)
            .order_by(Processo.data_abertura.desc())
            .all()
        )

    # -----------------------------------------------------------------
    # Serialização
    # -----------------------------------------------------------------

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
            "valor_causa": float(self.valor_causa) if self.valor_causa else None,
            "data_abertura": self.data_abertura.isoformat() if self.data_abertura else None,
            "prazo_final": self.prazo_final.isoformat() if self.prazo_final else None,
            "ativo": self.ativo,
        }

    def __repr__(self):
        return f"<Processo {self.id} - {self.numero_processo}>"
