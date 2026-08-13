"""
Registro central das rotas da API.

Regra da arquitetura: a rota aponta para o Controller e nada mais.
Não existe lógica de negocio nem SQL neste arquivo.
"""

import logging

from flask import Blueprint, jsonify
from sqlalchemy import text

from controllers.auth_controller import AuthController
from controllers.checklist_controller import ChecklistController
from controllers.cliente_controller import ClienteController
from controllers.processo_controller import ProcessoController
from controllers.documento_controller import DocumentoController
from controllers.importacao_controller import ImportacaoController
from controllers.notificacao_controller import NotificacaoController
from controllers.painel_controller import PainelController
from controllers.usuario_controller import UsuarioController
from extensions import db
from utils.autenticacao import carregar_usuario_da_requisicao

# ---------------------------------------------------------------------
# Diagnostico
# ---------------------------------------------------------------------
sistema_bp = Blueprint("sistema", __name__, url_prefix="/api")


@sistema_bp.get("/status")
def status():
    """Verifica se a API esta no ar e se o banco esta acessivel."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as erro:  # noqa: BLE001
        logging.getLogger("tabflower").error("Banco inacessivel: %s", erro)
        return (
            jsonify(
                {"api": "no ar", "banco": "sem conexão", "detalhe": str(erro)}
            ),
            500,
        )

    return jsonify({"api": "no ar", "banco": "conectado"}), 200


# ---------------------------------------------------------------------
# Autenticação
# Único Blueprint que fica público - é ele que devolve o token que
# todas as outras rotas passam a exigir.
# ---------------------------------------------------------------------
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

auth_bp.post("/login")(AuthController.login)


# ---------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------
cliente_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")

# Rotas de caminho fixo vem antes das rotas com parametro, senao o Flask
# tenta interpretar "busca" como se fosse um id.
cliente_bp.get("")(ClienteController.listar)
cliente_bp.get("/busca")(ClienteController.buscar_por_nome)
cliente_bp.get("/documento/<documento>")(ClienteController.buscar_por_documento)
cliente_bp.get("/<int:id_cliente>")(ClienteController.buscar_por_id)
cliente_bp.post("")(ClienteController.criar)
cliente_bp.put("/<int:id_cliente>")(ClienteController.atualizar)
cliente_bp.delete("/<int:id_cliente>")(ClienteController.excluir)


# ---------------------------------------------------------------------
# Processos
# ---------------------------------------------------------------------
processo_bp = Blueprint("processos", __name__, url_prefix="/api/processos")

processo_bp.get("")(ProcessoController.listar)
processo_bp.get("/opcoes")(ProcessoController.opcoes)
processo_bp.get("/busca")(ProcessoController.buscar)
processo_bp.get("/numero")(ProcessoController.buscar_por_numero)
processo_bp.get("/<int:id_processo>")(ProcessoController.buscar_por_id)
processo_bp.get("/<int:id_processo>/historico")(ProcessoController.historico)
processo_bp.get("/<int:id_processo>/checklist")(ProcessoController.checklist)
processo_bp.post("")(ProcessoController.criar)
processo_bp.put("/<int:id_processo>")(ProcessoController.atualizar)
processo_bp.patch("/<int:id_processo>/status")(ProcessoController.atualizar_status)
processo_bp.get("/<int:id_processo>/marcadores")(ProcessoController.listar_marcadores)
processo_bp.post("/<int:id_processo>/marcadores")(ProcessoController.aplicar_marcador)
processo_bp.delete("/<int:id_processo>/marcadores/<int:id_marcador>")(ProcessoController.remover_marcador)
processo_bp.delete("/<int:id_processo>")(ProcessoController.excluir)


# ---------------------------------------------------------------------
# Usuários
# ---------------------------------------------------------------------
usuario_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")

usuario_bp.get("")(UsuarioController.listar)
usuario_bp.get("/perfis")(UsuarioController.perfis)
usuario_bp.get("/advogados")(UsuarioController.listar_advogados)
usuario_bp.get("/eu")(AuthController.eu)
usuario_bp.get("/<int:id_usuario>")(UsuarioController.buscar_por_id)
usuario_bp.post("")(UsuarioController.criar)
usuario_bp.put("/<int:id_usuario>")(UsuarioController.atualizar)
usuario_bp.patch("/<int:id_usuario>/senha")(UsuarioController.alterar_senha)
usuario_bp.delete("/<int:id_usuario>")(UsuarioController.excluir)


# ---------------------------------------------------------------------
# Documentos
# ---------------------------------------------------------------------
documento_bp = Blueprint("documentos", __name__, url_prefix="/api/documentos")

documento_bp.get("")(DocumentoController.listar)
documento_bp.get("/categorias")(DocumentoController.categorias)
documento_bp.get("/<int:id_documento>")(DocumentoController.buscar_por_id)
documento_bp.get("/<int:id_documento>/arquivo")(DocumentoController.baixar)
documento_bp.post("")(DocumentoController.enviar)
documento_bp.put("/<int:id_documento>")(DocumentoController.atualizar)
documento_bp.patch("/<int:id_documento>/restaurar")(DocumentoController.restaurar)
documento_bp.delete("/<int:id_documento>")(DocumentoController.excluir)


# ---------------------------------------------------------------------
# Notificações
# ---------------------------------------------------------------------
notificacao_bp = Blueprint("notificacoes", __name__, url_prefix="/api/notificacoes")

notificacao_bp.get("")(NotificacaoController.listar)
notificacao_bp.patch("/<int:id_notificacao>/lida")(NotificacaoController.marcar_lida)


# ---------------------------------------------------------------------
# Painel - Terceira Etapa
# Todas estas rotas passam por Repository e chamam stored procedures.
# ---------------------------------------------------------------------
painel_bp = Blueprint("painel", __name__, url_prefix="/api/painel")

painel_bp.get("/resumo")(PainelController.resumo)
painel_bp.get("/pendencias")(PainelController.pendencias)
painel_bp.get("/prioritarios")(PainelController.prioritarios)
painel_bp.get("/marcadores")(PainelController.marcadores)


# ---------------------------------------------------------------------
# Configuração de checklist (Funcionalidade 13)
# ---------------------------------------------------------------------
checklist_bp = Blueprint("checklists", __name__, url_prefix="/api/checklists")

checklist_bp.get("/opcoes")(ChecklistController.opcoes)
checklist_bp.get("")(ChecklistController.listar)
checklist_bp.post("")(ChecklistController.adicionar)
checklist_bp.patch("/<int:id_item>/obrigatorio")(ChecklistController.alternar)
checklist_bp.delete("/<int:id_item>")(ChecklistController.remover)


# ---------------------------------------------------------------------
# Importação em lote (Funcionalidades 18 e 19)
# ---------------------------------------------------------------------
importacao_bp = Blueprint("importacoes", __name__, url_prefix="/api/importacoes")

importacao_bp.get("")(ImportacaoController.listar)
importacao_bp.get("/modelo")(ImportacaoController.modelo)
importacao_bp.get("/<int:id_importacao>/clientes")(ImportacaoController.clientes)
importacao_bp.post("")(ImportacaoController.importar)
importacao_bp.delete("/<int:id_importacao>")(ImportacaoController.desfazer)


def registrar_rotas(app):
    """Registra todos os Blueprints na aplicação.

    Todos exigem login, exceto o de status (diagnóstico) e o de auth
    (é ele que fornece o token). A proteção é aplicada aqui, uma única
    vez, em vez de em cada Controller - assim nenhuma rota nova corre o
    risco de esquecer a checagem.
    """
    blueprints_protegidos = (
        cliente_bp,
        processo_bp,
        usuario_bp,
        documento_bp,
        notificacao_bp,
        painel_bp,
        checklist_bp,
        importacao_bp,
    )
    for blueprint in blueprints_protegidos:
        blueprint.before_request(carregar_usuario_da_requisicao)

    app.register_blueprint(sistema_bp)
    app.register_blueprint(auth_bp)
    for blueprint in blueprints_protegidos:
        app.register_blueprint(blueprint)
