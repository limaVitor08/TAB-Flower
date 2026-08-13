"""
Caso de uso: anexar um documento a um processo.

E o caso de uso mais denso do sistema, porque uma única ação da secretaria
dispara quatro funcionalidades de uma vez:

  09 - Identificação de Categoria (o arquivo entra classificado)
  10 - Renomeação Automática (o sistema gera o nome padronizado)
  11 - Checklist Obrigatório (o item correspondente e marcado como entregue)
  17 - Direcionamento Automático (o advogado do processo e notificado)

Hoje isso e feito na mao: abrir o PDF, ver o que e, renomear, arrastar
para a pasta certa, riscar do checklist impresso e avisar o advogado.

## Atomicidade

Uma unica ação da secretaria escreve em quatro tabelas: documento,
checklist_processo, notificacao e (as vezes) processo + historico_status.

Todas essas escritas acontecem numa transação so, com um unico
db.session.commit() no fim. Se qualquer uma falhar, o rollback desfaz
todas: não existe documento gravado sem o checklist ter sido riscado, nem
processo que avançou de fase sem o documento que causou o avanço.

Antes, cada etapa gravava por conta propria. Se a terceira falhasse, as
duas primeiras já estavam no banco e ninguem tinha como saber disso.
"""

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

# O limite vem do Config, e não e escrito de novo aqui: se o valor fosse
# repetido, mudar um e esquecer o outro deixaria a API recusando 16 MB
# enquanto o Service acha que o limite e outro.
#
# O Flask ja barra a requisicao antes de chegar neste Service, usando o
# MAX_CONTENT_LENGTH. A checagem abaixo e a rede de seguranca de quem
# chamar o Service por outro caminho (o script de terminal, por exemplo).
TAMANHO_MAXIMO_BYTES = Config.MAX_CONTENT_LENGTH


class EnviarDocumentoService:
    """Válida, renomeia, grava em disco e propaga as consequências."""

    @staticmethod
    def executar(arquivo, dados, autor_id):
        """Anexa o documento.

        autor_id vem sempre de g.usuario_atual, num parâmetro próprio, e
        nunca de dentro de "dados". "dados" e o formulario que o navegador
        mandou, e nada que veio de fora pode dizer quem enviou o arquivo -
        senao bastaria alterar um campo no F12 para o documento aparecer
        como enviado por outra pessoa.
        """
        if arquivo is None or not arquivo.filename:
            raise ValueError("Nenhum arquivo foi enviado.")

        # --- Validação do arquivo ---
        extensao = extensao_do_arquivo(arquivo.filename)

        if extensao not in EXTENSOES_PERMITIDAS:
            permitidas = ", ".join(sorted(EXTENSOES_PERMITIDAS))
            raise ValueError(f"Extensão não permitida. Aceitos: {permitidas}.")

        # Mede o tamanho sem carregar o arquivo inteiro na memória.
        arquivo.stream.seek(0, os.SEEK_END)
        tamanho_bytes = arquivo.stream.tell()
        arquivo.stream.seek(0)

        if tamanho_bytes == 0:
            raise ValueError("O arquivo enviado está vazio.")

        if tamanho_bytes > TAMANHO_MAXIMO_BYTES:
            # A mensagem também sai do limite, para não sobrar um "16 MB"
            # escrito à mão que passaria a mentir se o valor mudasse.
            limite_mb = TAMANHO_MAXIMO_BYTES // (1024 * 1024)
            raise ValueError(f"O arquivo passa de {limite_mb} MB.")

        # --- Validação dos vinculos ---
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

        # Cliente vindo do legado pode não ter pasta. Cria agora.
        # Sem commit aqui: a alteração entra junto com o resto, no fim.
        if not cliente.caminho_pasta:
            cliente.caminho_pasta = criar_estrutura_cliente(
                cliente.nome, cliente.documento
            )

        # --- Funcionalidade 10: renomeação automática ---
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

        # --- A partir daqui, tudo entra num commit só ---
        try:
            # confirmar=False: o flush gera o id do documento (o checklist e
            # a notificação precisam dele) sem fechar a transação.
            documento.salvar(confirmar=False)

            avanco = None

            if processo:
                EnviarDocumentoService._marcar_checklist(
                    processo, categoria, documento
                )
                EnviarDocumentoService._notificar_advogado(
                    processo, categoria, documento
                )

                # Se este anexo fechou o checklist obrigatório, o processo
                # muda de fase sozinho. O Service devolve qual foi a nova
                # fase para a tela poder avisar o usuário - automação
                # escondida assusta quem está operando.
                avanco = AvancarStatusAutomaticoService.ao_completar_checklist(
                    processo, autor_id
                )

            db.session.commit()
        except Exception as erro:
            # Uma falha em qualquer etapa desfaz todas as anteriores, e o
            # arquivo já gravado sai do disco - senao ficaria um PDF orfao
            # na pasta do cliente, sem nenhum registro no banco.
            db.session.rollback()
            if os.path.exists(caminho_absoluto):
                os.remove(caminho_absoluto)
            logger.exception("Falha ao anexar documento: %s", erro)
            raise ValueError("Não foi possível registrar o documento.")

        return {"documento": documento, "avanco_status": avanco}

    # -----------------------------------------------------------------

    @staticmethod
    def _inteiro(valor):
        """Converte para int com seguranca.

        Os dados chegam de um formulario multipart, entao tudo vem como
        texto - inclusive os ids.
        """
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _marcar_checklist(processo, categoria, documento):
        """Funcionalidade 11: risca o item do checklist.

        Procura o item daquela categoria que ainda esta pendente. Se o
        documento não corresponde a nenhuma exigência do tipo de processo,
        nada acontece - o anexo e válido, só não abate pendência nenhuma.
        """
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
        # Sem commit: faz parte da transação do executar().

    @staticmethod
    def _notificar_advogado(processo, categoria, documento):
        """Funcionalidades 16 e 17: avisa quem e responsavel pelo caso.

        O sistema cruza o documento com o advogado_id do processo. Ninguem
        precisa lembrar de avisar, e o aviso não se perde numa conversa.

        O salvar() da Notificacao não confirma: o aviso entra junto com o
        documento que o originou, no commit do executar().
        """
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
