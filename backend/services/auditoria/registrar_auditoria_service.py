"""
Caso de uso: registrar uma ação sensível no log de auditoria.

Complementa a Funcionalidade 20 (Restrição de Exclusão). A tabela
log_auditoria existe desde a Primeira Etapa, mas só agora, com o login,
o sistema sabe quem de fato executou cada ação.

Por que a escrita fica num Service e não no Controller: o Controller só
traduz HTTP. Quem sabe que "isto foi uma exclusão de cliente" é o caso de
uso, e é ele quem chama este registro.

## Por que este Service NÃO faz commit

Este é o ponto que vale explicar na apresentação.

Se o registro de auditoria fosse gravado com um commit próprio, ele viraria
uma segunda transação: a exclusão poderia entrar e o log falhar, ou o
contrário. O banco ficaria dizendo que algo foi excluído sem ninguém ter
excluído, ou o oposto.

Em vez disso, o Service apenas coloca a linha na sessão (`db.session.add`).
Quem chama registra a auditoria ANTES de gravar a alteração, e o commit que
grava a alteração leva o log junto, na mesma transação. Ou os dois entram,
ou nenhum entra. Isso é atomicidade.
"""

from datetime import datetime

from extensions import db
from models.auditoria import LogAuditoria


class RegistrarAuditoriaService:
    """Prepara o registro de auditoria. O commit é de quem chama."""

    @staticmethod
    def registrar(usuario_id, acao, entidade, entidade_id=None, descricao=None):
        """Coloca uma linha de auditoria na sessão, sem gravar ainda.

        usuario_id  quem fez (vem sempre de g.usuario_atual, nunca da requisição)
        acao        CRIAR, ATUALIZAR, EXCLUIR, RESTAURAR, LOGIN ou DOWNLOAD
        entidade    nome da tabela afetada ("cliente", "processo", ...)
        entidade_id id da linha afetada
        descricao   texto curto para quem for ler o log depois
        """
        registro = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            # O banco corta em 255. Cortar aqui evita que um nome de cliente
            # muito longo derrube a operação inteira por causa do log.
            descricao=(descricao or "")[:255] or None,
            criado_em=datetime.now(),
        )

        db.session.add(registro)
        return registro
