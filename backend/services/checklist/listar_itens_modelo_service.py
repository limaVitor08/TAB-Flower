# Lista os documentos que o molde de um tipo de processo exige
from extensions import db
from models.checklist import ChecklistModelo
from models.tabelas_apoio import CategoriaDocumento, TipoProcesso


class ListarItensModeloService:
    @staticmethod
    def executar(tipo_processo_id):
        tipo = db.session.get(TipoProcesso, tipo_processo_id)
        if not tipo:
            raise LookupError("Tipo de processo não encontrado.")

        itens = ChecklistModelo.listar_do_tipo(tipo.id)
        categorias = {c.id: c for c in CategoriaDocumento.listar_todos()}

        resultado = []
        for item in itens:
            categoria = categorias.get(item.categoria_id)
            resultado.append(
                {
                    "id": item.id,
                    "tipo_processo_id": item.tipo_processo_id,
                    "categoria_id": item.categoria_id,
                    "categoria_nome": categoria.nome if categoria else None,
                    "categoria_sigla": categoria.sigla if categoria else None,
                    "obrigatorio": item.obrigatorio,
                    "ordem": item.ordem,
                }
            )
        return resultado
