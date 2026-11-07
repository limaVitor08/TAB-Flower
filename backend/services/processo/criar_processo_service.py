# Abre um processo novo com o checklist e a primeira fase
import logging
from datetime import date, datetime

from extensions import db
from models.checklist import ChecklistModelo, ChecklistProcesso
from models.cliente import Cliente
from models.processo import HistoricoStatus, Processo
from models.tabelas_apoio import StatusProcesso, TipoProcesso
from models.usuario import Usuario

logger = logging.getLogger("tabflower")


class CriarProcessoService:
    @staticmethod
    def executar(dados, criado_por=None):
        numero = (dados.get("numero_processo") or "").strip()
        titulo = (dados.get("titulo") or "").strip()

        if not numero:
            raise ValueError("O número do processo é obrigatório.")

        if not titulo:
            raise ValueError("O título do processo é obrigatório.")

        if Processo.buscar_por_numero(numero):
            raise ValueError("Já existe um processo com este número.")

        cliente = Cliente.buscar_por_id(dados.get("cliente_id"))
        if not cliente:
            raise ValueError("Cliente não encontrado.")

        advogado = Usuario.buscar_por_id(dados.get("advogado_id"))
        if not advogado:
            raise ValueError("Advogado responsável não encontrado.")

        if not advogado.perfil or advogado.perfil.nome != "Advogado":
            raise ValueError(
                "O responsável pelo processo precisa ter perfil de Advogado."
            )

        tipo = db.session.get(TipoProcesso, dados.get("tipo_processo_id"))
        if not tipo:
            raise ValueError("Tipo de processo inválido.")

        status_id = dados.get("status_id")
        if status_id:
            status = db.session.get(StatusProcesso, status_id)
            if not status:
                raise ValueError("Status inválido.")
        else:
            status = StatusProcesso.listar_todos()[0]

        processo = Processo(
            numero_processo=numero,
            titulo=titulo,
            descricao=(dados.get("descricao") or "").strip() or None,
            cliente_id=cliente.id,
            advogado_id=advogado.id,
            tipo_processo_id=tipo.id,
            status_id=status.id,
            comarca=(dados.get("comarca") or "").strip() or None,
            valor_causa=None if dados.get("valor_causa") in (None, "") else dados["valor_causa"],
            data_abertura=dados.get("data_abertura") or date.today(),
            prazo_final=dados.get("prazo_final") or None,
            criado_em=datetime.now(),
            ativo=True,
        )
        try:
            processo.salvar(confirmar=False)

            CriarProcessoService._montar_checklist(processo)

            HistoricoStatus(
                processo_id=processo.id,
                status_anterior_id=None,
                status_novo_id=status.id,
                usuario_id=criado_por,
                observacao="Processo cadastrado no sistema.",
                criado_em=datetime.now(),
            ).salvar(confirmar=False)

            db.session.commit()
        except Exception as erro:
            db.session.rollback()
            logger.exception("Falha ao criar processo %s: %s", numero, erro)
            raise ValueError("Não foi possível cadastrar o processo.")

        return processo

    @staticmethod
    def _montar_checklist(processo):
        itens = ChecklistModelo.listar_do_tipo(processo.tipo_processo_id)

        for item in itens:
            db.session.add(
                ChecklistProcesso(
                    processo_id=processo.id,
                    categoria_id=item.categoria_id,
                    obrigatorio=item.obrigatorio,
                    entregue=False,
                )
            )
