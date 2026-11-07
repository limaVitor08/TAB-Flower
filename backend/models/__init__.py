# Carrega todas as Models juntas para o SQLAlchemy entender as ligações entre elas
from models.cliente import Cliente
from models.tabelas_apoio import (
    CategoriaDocumento,
    Marcador,
    StatusProcesso,
    TipoProcesso,
)
from models.usuario import Perfil, Usuario
from models.processo import HistoricoStatus, Processo
from models.documento import Documento
from models.checklist import ChecklistModelo, ChecklistProcesso
from models.notificacao import Notificacao
from models.importacao import ImportacaoLote
from models.auditoria import LogAuditoria

__all__ = [
    "Cliente",
    "Perfil",
    "Usuario",
    "TipoProcesso",
    "StatusProcesso",
    "Marcador",
    "CategoriaDocumento",
    "Processo",
    "HistoricoStatus",
    "Documento",
    "ChecklistModelo",
    "ChecklistProcesso",
    "Notificacao",
    "ImportacaoLote",
    "LogAuditoria",
]
