"""
Desfaz uma importação (funcionalidade 19).
Quase nenhuma planilha antiga entra certa na primeira vez, e sem isso a
secretária teria que desativar cliente por cliente.
Só o Admin pode desfazer, porque isso desativa muitos clientes de uma
vez. Os clientes não são apagados, só desativados. E quem já tem algum
processo é mantido, porque já virou trabalho do escritório.
"""
from datetime import datetime
from extensions import db
from models.cliente import Cliente
from models.importacao import ImportacaoLote
from models.processo import Processo
class DesfazerImportacaoService:
    @staticmethod
    def executar(id_importacao, usuario_logado):
        if not usuario_logado.perfil or not usuario_logado.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario_logado.perfil.nome if usuario_logado.perfil else 'atual'} "
                "não tem permissão para desfazer importações. "
                "Somente o Administrador pode."
            )
        lote = ImportacaoLote.buscar_por_id(id_importacao)
        if not lote:
            raise LookupError("Importação não encontrada.")
        clientes = Cliente.query.filter_by(
            importacao_id=lote.id, ativo=True
        ).all()
        if not clientes:
            raise ValueError(
                "Nenhum cliente ativo desta importação para desfazer."
            )
        desativados = 0
        preservados = []
        for cliente in clientes:
            tem_processo = Processo.query.filter_by(
                cliente_id=cliente.id
            ).first()
            if tem_processo:
                preservados.append(cliente.nome)
                continue
            cliente.ativo = False
            cliente.atualizado_em = datetime.now()
            desativados += 1
        db.session.commit()
        return {
            "desativados": desativados,
            "preservados": preservados,
        }