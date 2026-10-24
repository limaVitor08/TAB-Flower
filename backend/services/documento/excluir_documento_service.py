"""
Exclui um documento (funcionalidade 20).

1 - Só o Admin pode excluir.
2 - A exclusão é só uma marcação, o registro e o arquivo continuam existindo.

Se o documento cobria um item do checklist, o item volta a ficar
pendente, e o processo pode voltar de fase. Isso tudo, junto com o log de
auditoria, entra num commit só. Assim o sistema nunca diz que a
documentação está completa depois que o arquivo que a completava saiu.
"""

import logging

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


class ExcluirDocumentoService:
    @staticmethod
    def executar(id_documento, usuario):
        """Exclui logicamente o documento.
        Recebe o objeto do usuário logado (g.usuario_atual), e não um id.
        """
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

            documento.remover(usuario_id=usuario.id, confirmar=False)

            retorno = None
            if documento.processo_id:
                processo = Processo.buscar_por_id(documento.processo_id)
                if processo:
                    retorno = AvancarStatusAutomaticoService.ao_reabrir_pendencia(
                        processo, usuario.id
                    )

            RegistrarAuditoriaService.registrar(
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
    def restaurar(id_documento, usuario):
        """Desfaz a exclusão. Restrito ao Admin."""
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")

        if not documento.excluido:
            raise ValueError("Este documento não está excluído.")

        if not usuario.perfil or not usuario.perfil.pode_excluir:
            raise PermissionError(
                "Somente o Administrador pode restaurar documentos."
            )

        RegistrarAuditoriaService.registrar(
            usuario_id=usuario.id,
            acao="RESTAURAR",
            entidade="documento",
            entidade_id=documento.id,
            descricao=f"Documento {documento.nome_padronizado} restaurado.",
        )

        return documento.restaurar()

    @staticmethod
    def _reabrir_pendencia(documento):
        """Se o documento atendia um item do checklist, ele volta a pendente."""
        item = ChecklistProcesso.query.filter_by(
            documento_id=documento.id
        ).first()

        if not item:
            return

        item.entregue = False
        item.entregue_em = None
        item.documento_id = None
