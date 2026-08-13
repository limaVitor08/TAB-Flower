"""
Model LogAuditoria.

Camada de Domínio / Persistência Simples.

Responde diretamente a dor levantada na entrevista com o escritório:
"o log de alterações e inexistente, entao quando algo some, não sabemos
quem moveu ou apagou". Complementa a Funcionalidade 20.

A tabela já existia no create_database.sql desde a Primeira Etapa, mas
nada escrevia nela - porque o sistema não sabia quem estava operando.
Agora que existe login, g.usuario_atual fornece o autor real de cada ação
e o registro passa a fazer sentido.

Esta Model e só de escrita e leitura: nada aqui altera ou remove linha.
Um log que pode ser editado não serve como log.
"""

from extensions import db


class LogAuditoria(db.Model):
    __tablename__ = "log_auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    acao = db.Column(
        db.Enum("CRIAR", "ATUALIZAR", "EXCLUIR", "RESTAURAR", "LOGIN", "DOWNLOAD"),
        nullable=False,
    )
    # Qual tabela foi afetada e qual linha dela. Guardar os dois separados
    # permite responder "o que aconteceu com o cliente 42?" sem precisar
    # ler texto livre.
    entidade = db.Column(db.String(50), nullable=False)
    entidade_id = db.Column(db.Integer)
    descricao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime)

    usuario = db.relationship("Usuario", lazy="joined")

    @staticmethod
    def listar_da_entidade(entidade, entidade_id):
        """Histórico de um registro específico, do mais novo para o mais antigo."""
        return (
            LogAuditoria.query.filter_by(entidade=entidade, entidade_id=entidade_id)
            .order_by(LogAuditoria.criado_em.desc())
            .all()
        )

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
