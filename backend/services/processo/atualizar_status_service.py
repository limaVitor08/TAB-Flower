"""
Muda a fase do processo (funcionalidade 7).

Tem um Service só para isso porque não é uma edição comum. Além de
trocar a fase, precisa registrar a mudança no histórico. É esse
histórico que substitui a planilha que o escritório usava.
"""

import logging
from datetime import datetime

from extensions import db
from models.processo import HistoricoStatus, Processo
from models.tabelas_apoio import StatusProcesso

logger = logging.getLogger("tabflower")


class AtualizarStatusService:
    @staticmethod
    def executar(
        id_processo,
        status_novo_id,
        usuario_id=None,
        observacao=None,
        confirmar=True,
    ):
        processo = Processo.buscar_por_id(id_processo)
        if not processo:
            raise LookupError("Processo não encontrado.")

        status_novo = db.session.get(StatusProcesso, status_novo_id)
        if not status_novo:
            raise ValueError("Status inválido.")

        if processo.status_id == status_novo.id:
            raise ValueError("O processo já está neste status.")

        status_anterior_id = processo.status_id
        processo.status_id = status_novo.id

        HistoricoStatus(
            processo_id=processo.id,
            status_anterior_id=status_anterior_id,
            status_novo_id=status_novo.id,
            usuario_id=usuario_id,
            observacao=(observacao or "").strip() or None,
            criado_em=datetime.now(),
        ).salvar(confirmar=False)

        if confirmar:
            try:
                db.session.commit()
            except Exception:
                # Sem o rollback, a sessão fica travada e a proxima
                # requisição herdaria o erro desta.
                db.session.rollback()
                logger.exception(
                    "Falha ao mudar o status do processo %s", id_processo
                )
                raise ValueError("Não foi possível atualizar a situação do processo.")

        return processo
