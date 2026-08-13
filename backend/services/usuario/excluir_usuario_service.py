"""
Caso de uso: desativar um usuário.

Funcionalidade 20 (Restricao de Exclusão).

Usuário nunca e apagado: processos apontam para o advogado responsavel e
o log de auditoria registra quem fez cada ação. Apagar quebraria as duas
coisas e destruiria a rastreabilidade que o escritório não tem hoje.
"""

from models.processo import Processo
from models.usuario import Usuario
from services.auditoria.registrar_auditoria_service import (
    RegistrarAuditoriaService,
)


class ExcluirUsuarioService:
    @staticmethod
    def executar(id_usuario, usuario_logado):
        if not usuario_logado.perfil or not usuario_logado.perfil.pode_excluir:
            raise PermissionError(
                f"O perfil {usuario_logado.perfil.nome if usuario_logado.perfil else 'atual'} "
                "não tem permissão para desativar usuários. "
                "Somente o Administrador pode."
            )

        # Ninguem se desativa. Se o unico Administrador se desativasse,
        # ninguem mais administraria o sistema - daria para recuperar pelo
        # criar_primeiro_usuario.py, mas evitar o problema e melhor do que
        # documentar a saida de emergencia.
        if usuario_logado.id == id_usuario:
            raise ValueError("Você não pode desativar a própria conta.")

        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")

        if not usuario.ativo:
            raise ValueError("Este usuário já está inativo.")

        # Um advogado com processos ativos não pode sumir do sistema sem
        # que alguem assuma os casos dele.
        pendentes = [
            p for p in Processo.query.filter_by(
                advogado_id=usuario.id, ativo=True
            ).all()
        ]

        if pendentes:
            raise ValueError(
                f"Este advogado responde por {len(pendentes)} processo(s) ativo(s). "
                "Transfira os processos para outro advogado antes de desativá-lo."
            )

        # Registrada antes do remover(): o commit do remover() grava a
        # desativação e o log na mesma transação.
        RegistrarAuditoriaService.registrar(
            usuario_id=usuario_logado.id,
            acao="EXCLUIR",
            entidade="usuario",
            entidade_id=usuario.id,
            descricao=f"Usuário {usuario.nome} desativado.",
        )

        return usuario.remover()
