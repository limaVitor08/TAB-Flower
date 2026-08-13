"""
Registro central das Models.

O SQLAlchemy só resolve chaves estrangeiras e relacoes entre tabelas se
TODAS as Models estiverem carregadas. Como algumas se referem a outras
pelo nome (checklist_processo aponta para documento, por exemplo), basta
uma ficar de fora para a aplicação quebrar ao subir, com um erro do tipo
"could not find table".

Importar tudo aqui resolve de uma vez: qualquer "from models.X import Y"
carrega este arquivo antes, e a partir dai o mapeamento esta montado.
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
