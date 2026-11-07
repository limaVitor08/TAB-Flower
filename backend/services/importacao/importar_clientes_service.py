# Importa clientes de uma planilha com as mesmas regras do cadastro
import logging
from datetime import datetime
from extensions import db
from models.importacao import ImportacaoLote
from services.cliente.criar_cliente_service import CriarClienteService
from utils.leitor_planilha import ErroLeitura, ler
COLUNAS = {
    "nome": ("nome", "cliente", "nome_do_cliente", "razao_social", "nome_completo"),
    "documento": ("documento", "cpf", "cnpj", "cpf_cnpj", "cpf_ou_cnpj"),
    "tipo_pessoa": ("tipo_pessoa", "tipo", "pessoa"),
    "email": ("email", "e_mail", "e_mail_1"),
    "telefone": ("telefone", "fone", "celular", "contato"),
    "endereco": ("endereco", "logradouro", "rua"),
    "cidade": ("cidade", "municipio"),
    "estado": ("estado", "uf"),
    "observacao": ("observacao", "observacoes", "obs", "anotacoes"),
}
LIMITE_LINHAS = 2000

LIMITE_RELATORIO = 60000
logger = logging.getLogger("tabflower")
UF_POR_NOME = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM",
    "bahia": "BA", "ceara": "CE", "distrito federal": "DF",
    "espirito santo": "ES", "goias": "GO", "maranhao": "MA",
    "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG",
    "para": "PA", "paraiba": "PB", "parana": "PR", "pernambuco": "PE",
    "piaui": "PI", "rio de janeiro": "RJ", "rio grande do norte": "RN",
    "rio grande do sul": "RS", "rondonia": "RO", "roraima": "RR",
    "santa catarina": "SC", "sao paulo": "SP", "sergipe": "SE",
    "tocantins": "TO",
}
def normalizar_uf(texto):
    import unicodedata
    bruto = (texto or "").strip()
    if not bruto:
        return ""
    if len(bruto) == 2:
        return bruto.upper()
    sem_acento = unicodedata.normalize("NFKD", bruto)
    sem_acento = sem_acento.encode("ASCII", "ignore").decode("ASCII").lower()
    sem_acento = " ".join(sem_acento.split())
    return UF_POR_NOME.get(sem_acento, bruto[:2].upper())
class ImportarClientesService:
    @staticmethod
    def executar(arquivo, usuario_id=None):
        if arquivo is None or not arquivo.filename:
            raise ValueError("Nenhum arquivo foi enviado.")
        conteudo = arquivo.read()
        if not conteudo:
            raise ValueError("O arquivo enviado está vazio.")
        try:
            linhas = ler(arquivo.filename, conteudo)
        except ErroLeitura as erro:
            raise ValueError(str(erro))
        if not linhas:
            raise ValueError("A planilha não tem nenhuma linha de dados.")
        if len(linhas) > LIMITE_LINHAS:
            raise ValueError(
                f"A planilha tem {len(linhas)} linhas. O limite por importação "
                f"é {LIMITE_LINHAS}. Divida o arquivo em partes."
            )
        lote = ImportacaoLote(
            usuario_id=usuario_id,
            nome_arquivo=arquivo.filename[:200],
            total_registros=len(linhas),
            situacao="PROCESSANDO",
            criado_em=datetime.now(),
        ).salvar()
        sucessos = 0
        erros = []
        for linha in linhas:
            indice = linha["_linha"]
            try:
                dados = ImportarClientesService._mapear(linha)
                cliente = CriarClienteService.executar(
                    dados, criado_por=usuario_id, confirmar=False
                )
                cliente.importacao_id = lote.id
                db.session.commit()
                sucessos += 1
            except ValueError as erro:
                db.session.rollback()
                nome = linha.get("nome") or linha.get("cliente") or "(sem nome)"
                erros.append(f"Linha {indice} ({nome}): {erro}")
            except Exception as erro:
                db.session.rollback()
                logger.exception(
                    "Erro inesperado na linha %s da importação %s", indice, lote.id
                )
                erros.append(
                    f"Linha {indice}: erro inesperado ao gravar. "
                    "O motivo ficou registrado no log do sistema."
                )
        situacao = "CONCLUIDA" if sucessos > 0 else "FALHOU"
        lote.finalizar(
            situacao, sucessos, len(erros), ImportarClientesService._relatorio(erros)
        )
        return lote
    @staticmethod
    def _relatorio(erros):
        linhas = []
        tamanho = 0
        for indice, erro in enumerate(erros):
            tamanho += len(erro.encode("utf-8")) + 1
            if tamanho > LIMITE_RELATORIO:
                restantes = len(erros) - indice
                linhas.append(
                    f"... e mais {restantes} linha(s) com problema, "
                    "que não couberam neste relatório."
                )
                break
            linhas.append(erro)
        return "\n".join(linhas) or None
    @staticmethod
    def _valor(linha, campo):
        for nome in COLUNAS[campo]:
            if linha.get(nome):
                return linha[nome].strip()
        return ""
    @staticmethod
    def _mapear(linha):
        documento = ImportarClientesService._valor(linha, "documento")
        tipo = ImportarClientesService._valor(linha, "tipo_pessoa").upper()
        if tipo not in ("F", "J"):
            somente_numeros = "".join(c for c in documento if c.isdigit())
            if len(somente_numeros) == 14:
                tipo = "J"
            elif len(somente_numeros) == 11:
                tipo = "F"
            elif tipo.startswith("J") or "JUR" in tipo:
                tipo = "J"
            else:
                tipo = "F"
        return {
            "nome": ImportarClientesService._valor(linha, "nome"),
            "tipo_pessoa": tipo,
            "documento": documento,
            "email": ImportarClientesService._valor(linha, "email"),
            "telefone": ImportarClientesService._valor(linha, "telefone"),
            "endereco": ImportarClientesService._valor(linha, "endereco"),
            "cidade": ImportarClientesService._valor(linha, "cidade"),
            "estado": normalizar_uf(ImportarClientesService._valor(linha, "estado")),
            "observacao": ImportarClientesService._valor(linha, "observacao"),
        }
