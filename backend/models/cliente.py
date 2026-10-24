"""
Model do Cliente.
Herda de db.Model, então já conversa com o banco pelo SQLAlchemy. Aqui
fica só o CRUD básico: salvar, atualizar, remover, buscar por id e
listar. Consulta mais complicada, com filtro ou JOIN, vai para o
Repository.
"""
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
    # -----------------------------------------------------------------
    # CRUD básico
    # -----------------------------------------------------------------
    def salvar(self, confirmar=True):
        """Insere o cliente no banco.
        confirmar=False e usado pela importação em lote: la o cliente e o
        vinculo com o lote precisam entrar na mesma transação, senao um
        cliente pode ficar gravado sem saber de qual carga veio, e o
        "Desfazer importação" nunca mais o alcança.
        """
        db.session.add(self)
        if confirmar:
            db.session.commit()
        else:
            db.session.flush()
        return self
    def atualizar(self, dados):
        """Altera apenas os campos enviados e grava.
        Campos que não podem ser alterados depois do cadastro ficam de
        fora da lista: mudar o documento burlaria o bloqueio de
        duplicidade da Funcionalidade 05.
        """
        campos_editaveis = [
            "nome",
            "email",
            "telefone",
            "endereco",
            "cidade",
            "estado",
            "observacao",
            "ativo",
        ]
        for campo in campos_editaveis:
            if campo in dados:
                setattr(self, campo, dados[campo])
        db.session.commit()
        return self
    def remover(self):
        """Desativa o cliente (exclusão lógica).
        O registro nunca sai da tabela por dois motivos:
        1. Processos e documentos apontam para o cliente. Apagar de
           verdade quebraria o histórico do escritório.
        2. A Funcionalidade 20 exige rastreabilidade do acervo.
        Clientes inativos deixam de aparecer nas listagens normais.
        """
        self.ativo = False
        db.session.commit()
        return self
    # -----------------------------------------------------------------
    # Consultas simples
    # -----------------------------------------------------------------
    @staticmethod
    def buscar_por_id(id_cliente):
        """Devolve o cliente pelo id, ou None se não existir."""
        return db.session.get(Cliente, id_cliente)
    @staticmethod
    def buscar_por_documento(documento):
        """Devolve o cliente pelo CPF/CNPJ, ou None.
        E este metodo que sustenta a Funcionalidade 05: antes de criar um
        cliente, o Service pergunta se o documento já existe.
        """
        return Cliente.query.filter_by(documento=documento).first()
    @staticmethod
    def listar_todos(apenas_ativos=True):
        """Lista os clientes em ordem alfabetica."""
        consulta = Cliente.query
        if apenas_ativos:
            consulta = consulta.filter_by(ativo=True)
        return consulta.order_by(Cliente.nome).all()
    # -----------------------------------------------------------------
    # Serialização
    # -----------------------------------------------------------------
    def to_dict(self):
        """Converte o cliente no formato JSON devolvido pela API."""
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