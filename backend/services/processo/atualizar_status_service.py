"""
Caso de uso: mudar a fase do processo.

Funcionalidade 07 (Atualizacao de Status).

Tem Service próprio porque não e uma edicao qualquer: além de gravar o
novo status, precisa registrar a mudanca no histórico. E o histórico e o
que substitui a planilha paralela do escritório.
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
        """Muda a fase do processo e registra a mudanca no histórico.

        As duas escritas andam juntas: um status novo sem linha no
        histórico deixaria o processo com uma fase que ninguem sabe quando
        nem por que mudou - exatamente o que a planilha do escritório fazia.

        confirmar=False quando esta mudanca e consequencia de outra
        operação (anexar ou excluir documento). Nesse caso o commit e do
        Service que comecou tudo, para as tabelas entrarem juntas.
        """
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
