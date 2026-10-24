"""
Importa clientes de uma planilha (funcionalidades 18 e 19).
Cada linha passa pelo mesmo CriarClienteService do cadastro manual, com
validação de CPF/CNPJ, bloqueio de repetido e criação da pasta. Se a
importação tivesse regras próprias, o cliente antigo entraria com
qualidade pior que o novo, e era justamente isso que queríamos evitar.
Uma linha com erro não derruba as outras. Cada linha tem o próprio
commit, e o erro fica anotado com o número da linha para a secretária
corrigir só o que falhou. Dentro de uma linha, o cliente e o vínculo com
o lote entram juntos. Senão o cliente ficaria sem saber de qual planilha
veio, e o "Desfazer importação" não ia encontrá-lo.
"""
import logging
from datetime import datetime
from extensions import db
from models.importacao import ImportacaoLote
from services.cliente.criar_cliente_service import CriarClienteService
from utils.leitor_planilha import ErroLeitura, ler
# Nomes de coluna aceitos para cada campo. A planilha do escritório
# raramente usa o mesmo cabeçalho do banco.
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
logger = logging.getLogger("tabflower")
# Planilhas de legado quase sempre trazem o estado por extenso. Sem esta
# conversão, "Minas Gerais" viraria "Mi" ao ser cortado em dois caracteres.
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
    """Converte o estado para a sigla de duas letras.
    Aceita "MG", "mg", "Minas Gerais" e "minas gerais". Se não reconhecer,
    devolve os dois primeiros caracteres em maiúscula, assim uma sigla
    desconhecida ainda entra, em vez de travar a linha inteira.
    """
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
        # O lote é registrado ANTES de processar, para que os clientes
        # criados já nasçam apontando para ele.
        lote = ImportacaoLote(
            usuario_id=usuario_id,
            nome_arquivo=arquivo.filename[:200],
            total_registros=len(linhas),
            situacao="PROCESSANDO",
            criado_em=datetime.now(),
        ).salvar()
        sucessos = 0
        erros = []
        for indice, linha in enumerate(linhas, start=2):  # linha 1 = cabeçalho
            try:
                dados = ImportarClientesService._mapear(linha)
                # confirmar=False: o cliente fica preparado, mas ainda não
                # gravado. Só depois de marcar a origem e que o commit
                # fecha as duas escritas de uma vez.
                cliente = CriarClienteService.executar(
                    dados, criado_por=usuario_id, confirmar=False
                )
                # Funcionalidade 19 marca a origem para permitir desfazer.
                cliente.importacao_id = lote.id
                db.session.commit()
                sucessos += 1
            except ValueError as erro:
                # Erro de validação (CPF inválido, cliente repetido) é
                # esperado numa planilha de legado, não vai para o log.
                db.session.rollback()
                nome = linha.get("nome") or linha.get("cliente") or "(sem nome)"
                erros.append(f"Linha {indice} ({nome}): {erro}")
            except Exception as erro:  # noqa: BLE001
                # Aqui e o inesperado. A secretaria ve so o numero da linha;
                # o motivo tecnico completo fica no tabflower.log, para
                # alguem conseguir investigar depois.
                db.session.rollback()
                logger.exception(
                    "Erro inesperado na linha %s da importação %s", indice, lote.id
                )
                erros.append(f"Linha {indice}: erro inesperado - {erro}")
        situacao = "CONCLUIDA" if sucessos > 0 else "FALHOU"
        lote.finalizar(situacao, sucessos, len(erros), "\n".join(erros) or None)
        return lote
    # -----------------------------------------------------------------
    @staticmethod
    def _valor(linha, campo):
        """Procura a coluna por qualquer um dos nomes aceitos."""
        for nome in COLUNAS[campo]:
            if linha.get(nome):
                return linha[nome].strip()
        return ""
    @staticmethod
    def _mapear(linha):
        """Converte uma linha da planilha no formato do CriarClienteService."""
        documento = ImportarClientesService._valor(linha, "documento")
        tipo = ImportarClientesService._valor(linha, "tipo_pessoa").upper()
        # Se a planilha não informa o tipo, deduz pela quantidade de
        # dígitos: 11 é CPF, 14 é CNPJ. É o caso mais comum no legado.
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