"""
Carrega todas as Models de uma vez.

O SQLAlchemy só entende as chaves estrangeiras se todas as Models
estiverem carregadas. Se uma ficar de fora, a aplicação quebra ao subir
com um erro do tipo "could not find table". Importando tudo aqui,
qualquer "from models.X import Y" já carrega o resto.
"""

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
