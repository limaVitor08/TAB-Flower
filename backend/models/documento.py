"""
Model Documento.

Camada de Domínio / Persistência Simples.

Representa o arquivo digitalizado. O PDF fica no disco do servidor; o
banco guarda o caminho, a categoria e o nome padronizado gerado pelo
sistema.

Funcionalidade 20 (Restricao de Exclusão): documento NUNCA e apagado da
tabela. O campo "excluido" e marcado e ficam registrados quem excluiu e
quando, para o acervo continuar rastreavel.
"""

from datetime import datetime

from extensions import db


class Documento(db.Model):
    __tablename__ = "documento"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"))
    categoria_id = db.Column(
        db.Integer, db.ForeignKey("categoria_documento.id"), nullable=False
    )
    nome_original = db.Column(db.String(200), nullable=False)
    nome_padronizado = db.Column(db.String(200), nullable=False)
    caminho_arquivo = db.Column(db.String(255), nullable=False, unique=True)
    extensao = db.Column(db.String(10), default="pdf")
    tamanho_kb = db.Column(db.Integer)
    enviado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    criado_em = db.Column(db.DateTime)
    excluido = db.Column(db.Boolean, nullable=False, default=False)
    excluido_em = db.Column(db.DateTime)
    excluido_por = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    categoria = db.relationship("CategoriaDocumento", lazy="joined")
    cliente = db.relationship("Cliente", lazy="joined")

    # -----------------------------------------------------------------
    # CRUD básico
    #
    # O parâmetro "confirmar" existe porque anexar e excluir documento não
    # são operações de uma tabela só: elas mexem também no checklist, na
    # notificação e no status do processo.
    #
    # confirmar=True  (padrão) - a Model grava sozinha, como Active Record.
    # confirmar=False          - a Model só prepara a escrita, e quem manda
    #                            no commit e o Service que comanda a
    #                            operação inteira. Assim, ou todas as
    #                            tabelas mudam, ou nenhuma muda.
    # -----------------------------------------------------------------

    def salvar(self, confirmar=True):
        db.session.add(self)
        if confirmar:
            db.session.commit()
        else:
            # flush envia o INSERT ao banco e devolve o id gerado, mas sem
            # fechar a transação - o documento ainda pode ser desfeito.
            db.session.flush()
        return self

    def atualizar(self, dados):
        """Só a categoria pode ser corrigida depois do envio.

        Nome e caminho do arquivo não mudam: eles apontam para um arquivo
        que já existe no disco.
        """
        if "categoria_id" in dados:
            self.categoria_id = dados["categoria_id"]

        db.session.commit()
        return self

    def remover(self, usuario_id=None, confirmar=True):
        """Exclusão lógica. O arquivo continua no disco."""
        self.excluido = True
        self.excluido_em = datetime.now()
        self.excluido_por = usuario_id
        if confirmar:
            db.session.commit()
        return self

    def restaurar(self, confirmar=True):
        self.excluido = False
        self.excluido_em = None
        self.excluido_por = None
        if confirmar:
            db.session.commit()
        return self

    # -----------------------------------------------------------------
    # Consultas simples
    # -----------------------------------------------------------------

    @staticmethod
    def buscar_por_id(id_documento):
        return db.session.get(Documento, id_documento)

    @staticmethod
    def listar_todos(incluir_excluidos=False):
        consulta = Documento.query
        if not incluir_excluidos:
            consulta = consulta.filter_by(excluido=False)
        return consulta.order_by(Documento.criado_em.desc()).all()

    @staticmethod
    def listar_do_processo(processo_id, incluir_excluidos=False):
        consulta = Documento.query.filter_by(processo_id=processo_id)
        if not incluir_excluidos:
            consulta = consulta.filter_by(excluido=False)
        return consulta.order_by(Documento.criado_em.desc()).all()

    @staticmethod
    def listar_do_cliente(cliente_id, incluir_excluidos=False):
        consulta = Documento.query.filter_by(cliente_id=cliente_id)
        if not incluir_excluidos:
            consulta = consulta.filter_by(excluido=False)
        return consulta.order_by(Documento.criado_em.desc()).all()

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente_nome": self.cliente.nome if self.cliente else None,
            "processo_id": self.processo_id,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria.nome if self.categoria else None,
            "nome_original": self.nome_original,
            "nome_padronizado": self.nome_padronizado,
            "extensao": self.extensao,
            "tamanho_kb": self.tamanho_kb,
            "excluido": self.excluido,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }

    def __repr__(self):
        return f"<Documento {self.id} - {self.nome_padronizado}>"
