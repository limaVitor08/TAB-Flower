# Desativa os clientes que entraram por um lote de importação
from datetime import datetime
from extensions import db
from models.cliente import Cliente
from models.importacao import ImportacaoLote
from models.processo import Processo
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)
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
        if desativados:
            RegistrarAuditoriaService.executar(
                usuario_id=usuario_logado.id,
                acao="EXCLUIR",
                entidade="importacao_lote",
                entidade_id=lote.id,
                descricao=(
                    f"Importação {lote.nome_arquivo} desfeita: "
                    f"{desativados} cliente(s) desativado(s)."
                ),
            )
        db.session.commit()
        return {
            "desativados": desativados,
            "preservados": preservados,
        }
