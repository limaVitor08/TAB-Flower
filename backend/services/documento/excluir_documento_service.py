# Marca um documento como excluído e reabre a pendência, só o Admin pode
import logging

from extensions import db
from models.checklist import ChecklistProcesso
from models.documento import Documento
from models.processo import Processo
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)
from services.processo.retroceder_status_automatico_service import (
    RetrocederStatusAutomaticoService,
)

logger = logging.getLogger("tabflower")


class ExcluirDocumentoService:
    @staticmethod
    def executar(id_documento, usuario):
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")

        if documento.excluido:
            raise ValueError("Este documento já foi excluído.")

        if not usuario.perfil or not usuario.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario.perfil.nome if usuario.perfil else 'atual'} "
                "não tem permissão para excluir documentos. "
                "Somente o Administrador pode."
            )

        try:
            ExcluirDocumentoService._reabrir_pendencia(documento)

            documento.deletar(usuario_id=usuario.id, confirmar=False)

            retorno = None
            if documento.processo_id:
                processo = Processo.buscar_por_id(documento.processo_id)
                if processo:
                    retorno = RetrocederStatusAutomaticoService.executar(
                        processo, usuario.id
                    )

            RegistrarAuditoriaService.executar(
                usuario_id=usuario.id,
                acao="EXCLUIR",
                entidade="documento",
                entidade_id=documento.id,
                descricao=f"Documento {documento.nome_padronizado} excluído.",
            )

            db.session.commit()
        except Exception as erro:
            db.session.rollback()
            logger.exception("Falha ao excluir documento %s: %s", id_documento, erro)
            raise ValueError("Não foi possível excluir o documento.")

        return {"documento": documento, "retorno_status": retorno}

    @staticmethod
    def _reabrir_pendencia(documento):
        item = ChecklistProcesso.query.filter_by(
            documento_id=documento.id
        ).first()

        if not item:
            return

        item.entregue = False
        item.entregue_em = None
        item.documento_id = None
