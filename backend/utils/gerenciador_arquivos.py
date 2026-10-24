"""
Cuida das pastas e dos nomes dos arquivos dos clientes.
Quando um cliente é cadastrado, criamos a pasta dele com as subpastas
padrão (funcionalidade 8). Quando chega um documento, é aqui que ele
ganha o nome padronizado e vai para a subpasta certa. Antes a secretária
fazia tudo isso na mão.
"""
import os
import re
import unicodedata
from config import Config
# Subpastas criadas para todo cliente novo.
SUBPASTAS_PADRAO = [
    "01_Documentos_Pessoais",
    "02_Procuracoes",
    "03_Contratos",
    "04_Processos",
    "05_Comprovantes",
    "06_Outros",
]
def normalizar_nome(texto):
    """Transforma o nome em algo seguro para usar como nome de pasta.
    'Jose da Silva & Cia' vira 'JOSE-DA-SILVA-CIA'.
    Isso evita acentos e simbolos que quebram caminhos no Windows.
    """
    if not texto:
        return "SEM-NOME"
    # Remove acentos: 'JOSÉ' -> 'JOSE'
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = sem_acento.encode("ASCII", "ignore").decode("ASCII")
    # Troca tudo que não for letra ou número por hifen.
    limpo = re.sub(r"[^A-Za-z0-9]+", "-", sem_acento)
    return limpo.strip("-").upper() or "SEM-NOME"
def montar_nome_pasta(nome, documento):
    """Monta o nome da pasta do cliente.
    Formato: NOME-DO-CLIENTE_DOCUMENTO
    O documento entra no nome para diferenciar clientes homonimos.
    """
    return f"{normalizar_nome(nome)}_{documento}"
def criar_estrutura_cliente(nome, documento):
    """Cria a pasta do cliente e suas subpastas.
    Devolve o caminho relativo que será gravado em cliente.caminho_pasta.
    Se a pasta já existir, nada e sobrescrito.
    """
    nome_pasta = montar_nome_pasta(nome, documento)
    caminho_completo = os.path.join(Config.PASTA_ARQUIVOS, nome_pasta)
    os.makedirs(caminho_completo, exist_ok=True)
    for subpasta in SUBPASTAS_PADRAO:
        os.makedirs(os.path.join(caminho_completo, subpasta), exist_ok=True)
    return nome_pasta
# ---------------------------------------------------------------------
# Renomeação e guarda de documentos
# Funcionalidades 09 (Identificação de Categoria) e 10 (Renomeação)
# ---------------------------------------------------------------------
# Em qual subpasta do cliente cada categoria de documento e guardada.
# A chave e a sigla cadastrada em categoria_documento.
SUBPASTA_POR_SIGLA = {
    "RG": "01_Documentos_Pessoais",
    "CPF": "01_Documentos_Pessoais",
    "CTPS": "01_Documentos_Pessoais",
    "PROC": "02_Procuracoes",
    "CTRT": "03_Contratos",
    "PETI": "04_Processos",
    "CERT": "04_Processos",
    "ENDR": "05_Comprovantes",
    "COMP": "05_Comprovantes",
    "LAUD": "06_Outros",
}
EXTENSOES_PERMITIDAS = {"pdf", "png", "jpg", "jpeg", "docx", "doc"}
def extensao_do_arquivo(nome_arquivo):
    """Devolve a extensão em minusculas, sem o ponto."""
    if "." not in (nome_arquivo or ""):
        return ""
    return nome_arquivo.rsplit(".", 1)[1].lower()
def montar_nome_padronizado(sigla, nome_cliente, data, extensao):
    """Monta o nome final do arquivo.
    Formato: SIGLA_NOME-DO-CLIENTE_AAAA-MM-DD.ext
    Exemplo: PROC_MARIA-DA-SILVA_2026-08-07.pdf
    E isto que substitui a renomeação manual: hoje a secretaria abre cada
    PDF escaneado, identifica o que e e digita o nome na mao.
    """
    return f"{sigla}_{normalizar_nome(nome_cliente)}_{data}.{extensao}"
def caminho_de_guarda(caminho_pasta_cliente, sigla):
    """Monta o caminho absoluto da subpasta onde o arquivo será gravado.
    Cria a pasta se ela não existir. Útil para clientes importados dos
    dados antigos, que podem não ter passado pela criação automática.
    """
    subpasta = SUBPASTA_POR_SIGLA.get(sigla, "06_Outros")
    destino = os.path.join(Config.PASTA_ARQUIVOS, caminho_pasta_cliente, subpasta)
    os.makedirs(destino, exist_ok=True)
    return destino, subpasta
def resolver_conflito(destino, nome_arquivo):
    """Evita sobrescrever arquivo existente.
    Se PROC_MARIA-DA-SILVA_2026-08-07.pdf já existe, o próximo vira
    PROC_MARIA-DA-SILVA_2026-08-07_2.pdf, e assim por diante.
    """
    if not os.path.exists(os.path.join(destino, nome_arquivo)):
        return nome_arquivo
    base, extensao = nome_arquivo.rsplit(".", 1)
    contador = 2
    while os.path.exists(os.path.join(destino, f"{base}_{contador}.{extensao}")):
        contador += 1
    return f"{base}_{contador}.{extensao}"