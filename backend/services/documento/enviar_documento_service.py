# Anexa um documento, renomeia, guarda na pasta certa e atualiza o checklist
import logging
from datetime import date, datetime

from config import Config
from extensions import db
from models.checklist import ChecklistProcesso
from models.cliente import Cliente
from models.documento import Documento
from models.notificacao import Notificacao
from models.processo import Processo
from models.tabelas_apoio import CategoriaDocumento
from services.processo.avancar_status_automatico_service import (
    AvancarStatusAutomaticoService,
)
from utils.gerenciador_arquivos import (
    EXTENSOES_PERMITIDAS,
    caminho_de_guarda,
    criar_estrutura_cliente,
    extensao_do_arquivo,
    montar_nome_padronizado,
    resolver_conflito,
)

import os

logger = logging.getLogger("tabflower")

TAMANHO_MAXIMO_BYTES = Config.MAX_CONTENT_LENGTH


class EnviarDocumentoService:
    @staticmethod
    def executar(arquivo, dados, autor_id):
        if arquivo is None or not arquivo.filename:
            raise ValueError("Nenhum arquivo foi enviado.")

        extensao = extensao_do_arquivo(arquivo.filename)

        if extensao not in EXTENSOES_PERMITIDAS:
            permitidas = ", ".join(sorted(EXTENSOES_PERMITIDAS))
            raise ValueError(f"Extensão não permitida. Aceitos: {permitidas}.")

        arquivo.stream.seek(0, os.SEEK_END)
        tamanho_bytes = arquivo.stream.tell()
        arquivo.stream.seek(0)

        if tamanho_bytes == 0:
            raise ValueError("O arquivo enviado está vazio.")

        if tamanho_bytes > TAMANHO_MAXIMO_BYTES:
            limite_mb = TAMANHO_MAXIMO_BYTES // (1024 * 1024)
            raise ValueError(f"O arquivo passa de {limite_mb} MB.")

        categoria = db.session.get(
            CategoriaDocumento, EnviarDocumentoService._inteiro(dados.get("categoria_id"))
        )
        if not categoria:
            raise ValueError("Categoria de documento inválida.")

        processo = None
        processo_id = EnviarDocumentoService._inteiro(dados.get("processo_id"))
        if processo_id:
            processo = Processo.buscar_por_id(processo_id)
            if not processo:
                raise ValueError("Processo não encontrado.")
            cliente = processo.cliente
        else:
            cliente = Cliente.buscar_por_id(
                EnviarDocumentoService._inteiro(dados.get("cliente_id"))
            )

        if not cliente:
            raise ValueError("Informe o processo ou o cliente do documento.")

        if not cliente.caminho_pasta:
            cliente.caminho_pasta = criar_estrutura_cliente(
                cliente.nome, cliente.documento
            )

        destino, subpasta = caminho_de_guarda(cliente.caminho_pasta, categoria.sigla)

        nome_padronizado = montar_nome_padronizado(
            categoria.sigla, cliente.nome, date.today().isoformat(), extensao
        )
        nome_padronizado = resolver_conflito(destino, nome_padronizado)

        caminho_absoluto = os.path.join(destino, nome_padronizado)
        caminho_relativo = os.path.join(
            cliente.caminho_pasta, subpasta, nome_padronizado
        ).replace("\\", "/")

        arquivo.save(caminho_absoluto)

        documento = Documento(
            cliente_id=cliente.id,
            processo_id=processo.id if processo else None,
            categoria_id=categoria.id,
            nome_original=arquivo.filename[:200],
            nome_padronizado=nome_padronizado,
            caminho_arquivo=caminho_relativo,
            extensao=extensao,
            tamanho_kb=max(1, round(tamanho_bytes / 1024)),
            enviado_por=autor_id,
            criado_em=datetime.now(),
            excluido=False,
        )

        try:
            documento.salvar(confirmar=False)

            avanco = None

            if processo:
                EnviarDocumentoService._marcar_checklist(
                    processo, categoria, documento
                )
                EnviarDocumentoService._notificar_advogado(
                    processo, categoria, documento
                )

                avanco = AvancarStatusAutomaticoService.executar(
                    processo, autor_id
                )

            db.session.commit()
        except Exception as erro:
            db.session.rollback()
            if os.path.exists(caminho_absoluto):
                os.remove(caminho_absoluto)
            logger.exception("Falha ao anexar documento: %s", erro)
            raise ValueError("Não foi possível registrar o documento.")

        return {"documento": documento, "avanco_status": avanco}


    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _marcar_checklist(processo, categoria, documento):
        item = ChecklistProcesso.query.filter_by(
            processo_id=processo.id,
            categoria_id=categoria.id,
            entregue=False,
        ).first()

        if not item:
            return

        item.entregue = True
        item.entregue_em = datetime.now()
        item.documento_id = documento.id

    @staticmethod
    def _notificar_advogado(processo, categoria, documento):
        Notificacao(
            usuario_destino_id=processo.advogado_id,
            processo_id=processo.id,
            documento_id=documento.id,
            titulo=f"Novo documento em {processo.numero_processo}",
            mensagem=f"Documento \"{categoria.nome}\" anexado ao processo {processo.titulo}."[:255],
            tipo="DOCUMENTO",
            lida=False,
            criado_em=datetime.now(),
        ).salvar()
