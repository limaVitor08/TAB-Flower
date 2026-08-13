"""
Models das tabelas de apoio.

São tabelas pequenas e estaveis, carregadas junto com o banco: tipos de
processo, status, marcadores e categorias de documento. Elas alimentam
os selects das telas e não possuem CRUD próprio nesta etapa.
"""

from extensions import db


class TipoProcesso(db.Model):
    __tablename__ = "tipo_processo"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    @staticmethod
    def listar_todos():
        return TipoProcesso.query.filter_by(ativo=True).order_by(TipoProcesso.nome).all()

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "descricao": self.descricao}


class StatusProcesso(db.Model):
    __tablename__ = "status_processo"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.String(200))
    cor_hex = db.Column(db.String(7))
    ordem = db.Column(db.Integer, default=0)
    is_final = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    @staticmethod
    def listar_todos():
        return (
            StatusProcesso.query.filter_by(ativo=True)
            .order_by(StatusProcesso.ordem)
            .all()
        )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cor_hex": self.cor_hex,
            "ordem": self.ordem,
            "is_final": self.is_final,
        }


class Marcador(db.Model):
    __tablename__ = "marcador"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    cor_hex = db.Column(db.String(7))
    peso = db.Column(db.Integer, default=0)

    @staticmethod
    def listar_todos():
        return Marcador.query.order_by(Marcador.peso.desc()).all()

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cor_hex": self.cor_hex,
            "peso": self.peso,
        }


class CategoriaDocumento(db.Model):
    __tablename__ = "categoria_documento"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    @staticmethod
    def listar_todos():
        return (
            CategoriaDocumento.query.filter_by(ativo=True)
            .order_by(CategoriaDocumento.nome)
            .all()
        )

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "sigla": self.sigla}
