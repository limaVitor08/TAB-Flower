"""
Model Notificação.

Funcionalidade 16 (Disparo de Notificações) e 17 (Direcionamento
Automático). Quando um documento e anexado a um processo, o sistema
descobre sozinho quem e o advogado responsavel e cria o aviso para ele.
Hoje isso e feito por e-mail informal ou no grito, e se perde.
"""

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
        """Grava o aviso.

        O padrão aqui e confirmar=False, ao contrario das outras Models: a
        notificação nunca nasce sozinha, ela e sempre consequencia de outra
        coisa (um documento anexado, por exemplo). Quem comanda o commit e
        o Service dono daquela operação - senao o aviso poderia ser gravado
        para um documento que acabou não entrando.
        """
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

    @staticmethod
    def listar_do_usuario(usuario_id, apenas_nao_lidas=False):
        consulta = Notificacao.query.filter_by(usuario_destino_id=usuario_id)
        if apenas_nao_lidas:
            consulta = consulta.filter_by(lida=False)
        return consulta.order_by(Notificacao.criado_em.desc()).all()

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
