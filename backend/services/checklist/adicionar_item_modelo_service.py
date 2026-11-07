# Acrescenta um documento exigido ao molde do checklist
from extensions import db
from models.checklist import ChecklistModelo
from models.tabelas_apoio import CategoriaDocumento, TipoProcesso
from services.checklist.listar_itens_modelo_service import ListarItensModeloService


class AdicionarItemModeloService:
    @staticmethod
    def executar(dados):
        tipo = db.session.get(TipoProcesso, dados.get("tipo_processo_id"))
        if not tipo:
            raise ValueError("Tipo de processo inválido.")

        categoria = db.session.get(CategoriaDocumento, dados.get("categoria_id"))
        if not categoria:
            raise ValueError("Categoria de documento inválida.")

        ja_existe = ChecklistModelo.query.filter_by(
            tipo_processo_id=tipo.id, categoria_id=categoria.id
        ).first()
        if ja_existe:
            raise ValueError(
                f"{categoria.nome} já é exigido para processos do tipo {tipo.nome}."
            )

        ultimo = (
            ChecklistModelo.query.filter_by(tipo_processo_id=tipo.id)
            .order_by(ChecklistModelo.ordem.desc())
            .first()
        )

        item = ChecklistModelo(
            tipo_processo_id=tipo.id,
            categoria_id=categoria.id,
            obrigatorio=bool(dados.get("obrigatorio", True)),
            ordem=(ultimo.ordem + 1) if ultimo else 1,
        )
        db.session.add(item)
        db.session.commit()

        return ListarItensModeloService.executar(tipo.id)
