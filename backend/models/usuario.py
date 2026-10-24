"""
Models de Perfil e de Usuário.
O usuário é quem entra no sistema: Admin, Advogado ou Secretária. Quem
tem perfil de Advogado também é o responsável pelos processos e quem
recebe as notificações.
"""
from extensions import db
class Perfil(db.Model):
    """Nível de permissão. Tabela de apoio, carregada junto com o banco."""
    __tablename__ = "perfil"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(150))
    pode_excluir = db.Column(db.Boolean, nullable=False, default=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    @staticmethod
    def listar_todos():
        return Perfil.query.filter_by(ativo=True).order_by(Perfil.id).all()
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "pode_excluir": self.pode_excluir,
        }
class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil_id = db.Column(db.Integer, db.ForeignKey("perfil.id"), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime)
    atualizado_em = db.Column(db.DateTime)
    perfil = db.relationship("Perfil", lazy="joined")
    # -----------------------------------------------------------------
    # CRUD básico
    # -----------------------------------------------------------------
    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self
    def atualizar(self, dados):
        """Altera os campos permitidos. A senha tem caminho próprio."""
        for campo in ("nome", "email", "perfil_id", "ativo"):
            if campo in dados:
                setattr(self, campo, dados[campo])
        db.session.commit()
        return self
    def remover(self):
        """Desativa o usuário.
        Não apagamos de verdade porque processos apontam para o advogado
        responsavel e o log de auditoria aponta para quem fez cada ação.
        """
        self.ativo = False
        db.session.commit()
        return self
    # -----------------------------------------------------------------
    # Consultas simples
    # -----------------------------------------------------------------
    @staticmethod
    def buscar_por_id(id_usuario):
        return db.session.get(Usuario, id_usuario)
    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=email).first()
    @staticmethod
    def listar_todos(apenas_ativos=True):
        consulta = Usuario.query
        if apenas_ativos:
            consulta = consulta.filter_by(ativo=True)
        return consulta.order_by(Usuario.nome).all()
    @staticmethod
    def listar_advogados():
        """Usuários que podem ser responsaveis por um processo."""
        return (
            Usuario.query.join(Perfil)
            .filter(Perfil.nome == "Advogado", Usuario.ativo.is_(True))
            .order_by(Usuario.nome)
            .all()
        )
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "perfil_id": self.perfil_id,
            "perfil_nome": self.perfil.nome if self.perfil else None,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
    def __repr__(self):
        return f"<Usuario {self.id} - {self.nome}>"