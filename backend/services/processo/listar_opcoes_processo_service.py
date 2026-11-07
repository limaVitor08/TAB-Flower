# Junta as opções que o formulário de processo precisa numa chamada só
from models.tabelas_apoio import StatusProcesso, TipoProcesso
from models.usuario import Usuario


class ListarOpcoesProcessoService:
    @staticmethod
    def executar():
        return {
            "tipos": TipoProcesso.listar_todos(),
            "status": StatusProcesso.listar_todos(),
            "advogados": Usuario.listar_advogados(),
        }
