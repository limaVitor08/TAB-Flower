"""
Caso de uso: desfazer uma importação.

Funcionalidade 19 (Organização de Legado).

Uma carga de legado quase nunca sai perfeita na primeira tentativa. Sem
poder desfazer, a secretária teria que desativar cliente por cliente
para tentar de novo.

Três regras:

  1. Só quem pode excluir (hoje, o Admin) desfaz uma importação. Esta
     rota desativa dezenas de clientes de uma vez: seria incoerente
     bloquear a Secretária ao desativar UM cliente pela tela e liberar a
     mesma pessoa para desativar a carga inteira por aqui.

  2. A exclusão é lógica, como em todo o resto do sistema. Os clientes
     ficam inativos, não somem.

  3. Cliente que já tem processo NÃO é desativado. Se alguém importou e
     depois abriu um processo para aquela pessoa, o cadastro deixou de
     ser "legado bruto" e passou a ser parte do trabalho do escritório.
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
