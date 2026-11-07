# Model do cliente, com o cadastro básico e as consultas simples
from extensions import db
from utils.validador_documento import formatar_documento
class Cliente(db.Model):
    __tablename__ = "cliente"
    id = db.Column(db.Integer, primary_key=True)
    tipo_pessoa = db.Column(db.Enum("F", "J"), nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    documento = db.Column(db.String(14), nullable=False, unique=True)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(80))
    estado = db.Column(db.String(2))
    caminho_pasta = db.Column(db.String(255))
    observacao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    importacao_id = db.Column(db.Integer)
    criado_por = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime)
    atualizado_em = db.Column(db.DateTime)
    def salvar(self, confirmar=True):
        db.session.add(self)
        if confirmar:
            db.session.commit()
        else:
            db.session.flush()
        return self
    def atualizar(self, dados):
        campos_editaveis = [
            "nome",
            "email",
            "telefone",
            "endereco",
            "cidade",
            "estado",
            "observacao",
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
    def buscar_por_id(id_cliente):
        return db.session.get(Cliente, id_cliente)
    @staticmethod
    def buscar_por_documento(documento):
        return Cliente.query.filter_by(documento=documento).first()
    @staticmethod
    def listar_todos(apenas_ativos=True):
        consulta = Cliente.query
        if apenas_ativos:
            consulta = consulta.filter_by(ativo=True)
        return consulta.order_by(Cliente.nome).all()
    def to_dict(self):
        return {
            "id": self.id,
            "tipo_pessoa": self.tipo_pessoa,
            "nome": self.nome,
            "documento": self.documento,
            "documento_formatado": formatar_documento(
                self.documento, self.tipo_pessoa
            ),
            "email": self.email,
            "telefone": self.telefone,
            "endereco": self.endereco,
            "cidade": self.cidade,
            "estado": self.estado,
            "caminho_pasta": self.caminho_pasta,
            "observacao": self.observacao,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
    def __repr__(self):
        return f"<Cliente {self.id} - {self.nome}>"
