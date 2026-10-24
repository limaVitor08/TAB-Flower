"""Atualiza os dados de um processo."""

from models.processo import Processo
from models.usuario import Usuario


class AtualizarProcessoService:
    @staticmethod
    def executar(id_processo, dados):
        processo = Processo.buscar_por_id(id_processo)
        if not processo:
            raise LookupError("Processo não encontrado.")

        if "numero_processo" in dados:
            novo = str(dados["numero_processo"]).strip()
            if novo and novo != processo.numero_processo:
                raise ValueError(
                    "O número do processo não pode ser alterado."
                )

        if "titulo" in dados and not (dados["titulo"] or "").strip():
            raise ValueError("O título do processo é obrigatório.")

        # Trocar de advogado responsavel e permitido, mas o novo também
        # precisa ter perfil de Advogado.
        if dados.get("advogado_id"):
            advogado = Usuario.buscar_por_id(dados["advogado_id"])
            if not advogado:
                raise ValueError("Advogado responsável não encontrado.")
            if not advogado.perfil or advogado.perfil.nome != "Advogado":
                raise ValueError(
                    "O responsável pelo processo precisa ter perfil de Advogado."
                )

        return processo.atualizar(dados)
