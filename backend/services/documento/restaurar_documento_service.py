# Desfaz a exclusão de um documento e devolve ele ao checklist
import logging
from datetime import datetime

from extensions import db
from models.checklist import ChecklistProcesso
from models.documento import Documento
from models.processo import Processo
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)
from services.processo.avancar_status_automatico_service import (
    AvancarStatusAutomaticoService,
)

logger = logging.getLogger("tabflower")


class RestaurarDocumentoService:
    @staticmethod
    def executar(id_documento, usuario):
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")

        if not documento.excluido:
            raise ValueError("Este documento não está excluído.")

        if not usuario.perfil or not usuario.perfil.pode_excluir:
            raise PermissionError(
                "Somente o Administrador pode restaurar documentos."
            )

        try:
            documento.restaurar(confirmar=False)

            avanco = None
            if documento.processo_id:
                processo = Processo.buscar_por_id(documento.processo_id)
                if processo:
                    RestaurarDocumentoService._devolver_ao_checklist(documento)
                    avanco = AvancarStatusAutomaticoService.executar(
                        processo, usuario.id
                    )

            RegistrarAuditoriaService.executar(
                usuario_id=usuario.id,
                acao="RESTAURAR",
                entidade="documento",
                entidade_id=documento.id,
                descricao=f"Documento {documento.nome_padronizado} restaurado.",
            )

            db.session.commit()
        except Exception as erro:
            db.session.rollback()
            logger.exception("Falha ao restaurar documento %s: %s", id_documento, erro)
            raise ValueError("Não foi possível restaurar o documento.")

        return {"documento": documento, "avanco_status": avanco}

    @staticmethod
    def _devolver_ao_checklist(documento):
        item = ChecklistProcesso.query.filter_by(
            processo_id=documento.processo_id,
            categoria_id=documento.categoria_id,
            entregue=False,
        ).first()

        if not item:
            return

        item.entregue = True
        item.entregue_em = datetime.now()
        item.documento_id = documento.id
