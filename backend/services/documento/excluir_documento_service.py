"""
Caso de uso: excluir um documento.

Funcionalidade 20 (Restricao de Exclusão). E o caso de uso que responde
diretamente a dor levantada na entrevista: "o log de alterações e
inexistente, entao quando algo some, não sabemos quem moveu ou apagou".

Duas travas:
  1. Somente perfis com pode_excluir = TRUE (hoje, apenas o Admin).
  2. A exclusão e lógica. O registro e o arquivo continuam existindo.

Se o documento abatia uma pendência do checklist, a pendência volta a
aparecer - senao o processo pareceria completo sem estar.

## Atomicidade

Excluir um documento mexe em ate quatro tabelas: documento,
checklist_processo, processo (status), historico_status - mais o
log_auditoria. Tudo entra num commit so. Se o processo não conseguisse
voltar de fase, o documento também não seria marcado como excluido: o
sistema nunca fica dizendo que a documentação esta completa quando o
arquivo que a completava sumiu.
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

        Recebe o objeto do usuário logado (g.usuario_atual), e não um id:
        quem chamou já autenticou essa pessoa, então buscá-la no banco de
        novo seria uma consulta a mais para chegar ao mesmo lugar. É o
        mesmo formato dos Services de exclusão de cliente e de processo.
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

            # Contrapartida do avanço automático: se o processo tinha subido
            # de fase por estar completo, ele volta para "aguardando".
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
        """Desfaz a exclusão. Também restrito ao Admin."""
        documento = Documento.buscar_por_id(id_documento)
        if not documento:
            raise LookupError("Documento não encontrado.")

        if not documento.excluido:
            raise ValueError("Este documento não está excluído.")

        if not usuario.perfil or not usuario.perfil.pode_excluir:
            raise PermissionError(
                "Somente o Administrador pode restaurar documentos."
            )

        # Auditoria antes: o commit do restaurar() grava as duas coisas.
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
        # Sem commit: faz parte da transação do executar().
