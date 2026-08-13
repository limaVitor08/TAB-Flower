"""
Caso de uso: aplicar e remover marcadores de um processo.

Funcionalidade 14 - Marcadores Visuais.

Os marcadores são fixos, definidos pelo sistema (Urgente, Prioridade,
Prazo curto). O usuário não cria marcadores novos, apenas aplica os que
existem - e cada um tem um peso, que e o que ordena o painel de
prioridades.
"""

from datetime import datetime

from sqlalchemy import text

from extensions import db
from models.processo import Processo
from models.tabelas_apoio import Marcador
from utils.conversao import converter_linhas


class MarcadoresService:

    @staticmethod
    def listar_do_processo(processo_id):
        """Marcadores aplicados a um processo."""
        resultado = db.session.execute(
            text(
                "SELECT m.id, m.nome, m.cor_hex, m.peso "
                "FROM processo_marcador pm "
                "INNER JOIN marcador m ON m.id = pm.marcador_id "
                "WHERE pm.processo_id = :pid "
                "ORDER BY m.peso DESC"
            ),
            {"pid": processo_id},
        )
        return converter_linhas(resultado)

    @staticmethod
    def aplicar(processo_id, marcador_id, usuario_id=None):
        processo = Processo.buscar_por_id(processo_id)
        if not processo:
            raise LookupError("Processo não encontrado.")

        marcador = db.session.get(Marcador, marcador_id)
        if not marcador:
            raise ValueError("Marcador inválido.")

        ja_aplicado = db.session.execute(
            text(
                "SELECT 1 FROM processo_marcador "
                "WHERE processo_id = :pid AND marcador_id = :mid"
            ),
            {"pid": processo_id, "mid": marcador_id},
        ).first()

        if ja_aplicado:
            raise ValueError("Este marcador já foi aplicado ao processo.")

        db.session.execute(
            text(
                "INSERT INTO processo_marcador "
                "(processo_id, marcador_id, aplicado_por, aplicado_em) "
                "VALUES (:pid, :mid, :uid, :quando)"
            ),
            {
                "pid": processo_id,
                "mid": marcador_id,
                "uid": usuario_id,
                "quando": datetime.now(),
            },
        )
        db.session.commit()

        return MarcadoresService.listar_do_processo(processo_id)

    @staticmethod
    def remover(processo_id, marcador_id):
        """Tira um marcador do processo.

        Diferente do resto do sistema, aqui a exclusão é física. O motivo
        é a natureza da tabela: processo_marcador é uma tabela de VÍNCULO,
        não de registro de negócio. Ela guarda "este processo está com a
        etiqueta Urgente", e tirar a etiqueta é desfazer o vínculo, não
        apagar um documento ou um cliente.

        Marcá-lo como inativo exigiria uma coluna nova e um filtro em toda
        consulta que usa marcadores - inclusive dentro da procedure
        sp_processos_prioritarios - sem nada a ganhar: ninguém precisa
        saber que um processo já teve a etiqueta Urgente no mês passado.

        É o mesmo raciocínio já aplicado ao molde de checklist, em
        services/checklist/gerenciar_modelo_service.py.
        """
        resultado = db.session.execute(
            text(
                "DELETE FROM processo_marcador "
                "WHERE processo_id = :pid AND marcador_id = :mid"
            ),
            {"pid": processo_id, "mid": marcador_id},
        )
        db.session.commit()

        if resultado.rowcount == 0:
            raise LookupError("Este marcador não estava aplicado ao processo.")

        return MarcadoresService.listar_do_processo(processo_id)
