"""
Configuração do checklist de cada tipo de processo (funcionalidade 13).
Aqui o escritório escolhe quais documentos cada tipo de processo exige.
Antes desta tela, só dava para mudar isso com INSERT direto no banco.
Mudar o molde não mexe nos processos que já existem. O molde só é
copiado quando o processo é aberto, então um processo do mês passado
continua com as exigências daquela época.
"""
from extensions import db
from models.checklist import ChecklistModelo, ChecklistProcesso
from models.tabelas_apoio import CategoriaDocumento, TipoProcesso
class GerenciarModeloService:
    @staticmethod
    def listar(tipo_processo_id):
        """Itens exigidos por um tipo de processo."""
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
    @staticmethod
    def adicionar(dados):
        """Acrescenta uma exigência ao tipo de processo."""
        tipo = db.session.get(TipoProcesso, dados.get("tipo_processo_id"))
        if not tipo:
            raise ValueError("Tipo de processo inválido.")
        categoria = db.session.get(CategoriaDocumento, dados.get("categoria_id"))
        if not categoria:
            raise ValueError("Categoria de documento inválida.")
        # O banco tem UNIQUE(tipo_processo_id, categoria_id), mas conferir
        # aqui devolve uma mensagem legível em vez de erro de integridade.
        ja_existe = ChecklistModelo.query.filter_by(
            tipo_processo_id=tipo.id, categoria_id=categoria.id
        ).first()
        if ja_existe:
            raise ValueError(
                f"{categoria.nome} já é exigido para processos do tipo {tipo.nome}."
            )
        # A nova exigência entra no fim da lista.
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
        return GerenciarModeloService.listar(tipo.id)
    @staticmethod
    def alternar_obrigatorio(id_item):
        """Troca a exigência entre obrigatória e opcional."""
        item = db.session.get(ChecklistModelo, id_item)
        if not item:
            raise LookupError("Item de checklist não encontrado.")
        item.obrigatorio = not item.obrigatorio
        db.session.commit()
        return GerenciarModeloService.listar(item.tipo_processo_id)
    @staticmethod
    def remover(id_item):
        """Tira uma exigência do molde.
        Diferente do resto do sistema, aqui a exclusão é física: o molde é
        configuração, não histórico. Nenhum processo perde dados, porque
        os checklists já criados são cópias independentes.
        """
        item = db.session.get(ChecklistModelo, id_item)
        if not item:
            raise LookupError("Item de checklist não encontrado.")
        tipo_id = item.tipo_processo_id
        db.session.delete(item)
        db.session.commit()
        return GerenciarModeloService.listar(tipo_id)
    @staticmethod
    def contar_processos_afetados(tipo_processo_id):
        """Quantos checklists já existentes NÃO mudam com esta alteração.
        Serve para a tela deixar claro que o molde vale só daqui pra frente.
        """
        return (
            db.session.query(ChecklistProcesso.processo_id)
            .join(
                ChecklistModelo,
                ChecklistModelo.categoria_id == ChecklistProcesso.categoria_id,
            )
            .filter(ChecklistModelo.tipo_processo_id == tipo_processo_id)
            .distinct()
            .count()
        )