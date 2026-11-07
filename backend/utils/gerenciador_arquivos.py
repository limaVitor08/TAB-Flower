# Cria as pastas dos clientes e monta o nome padronizado dos arquivos
import os
import re
import unicodedata
from config import Config
SUBPASTAS_PADRAO = [
    "01_Documentos_Pessoais",
    "02_Procuracoes",
    "03_Contratos",
    "04_Processos",
    "05_Comprovantes",
    "06_Outros",
]
def normalizar_nome(texto):
    if not texto:
        return "SEM-NOME"
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = sem_acento.encode("ASCII", "ignore").decode("ASCII")
    limpo = re.sub(r"[^A-Za-z0-9]+", "-", sem_acento)
    return limpo.strip("-").upper() or "SEM-NOME"
def montar_nome_pasta(nome, documento):
    return f"{normalizar_nome(nome)}_{documento}"
def criar_estrutura_cliente(nome, documento):
    nome_pasta = montar_nome_pasta(nome, documento)
    caminho_completo = os.path.join(Config.PASTA_ARQUIVOS, nome_pasta)
    os.makedirs(caminho_completo, exist_ok=True)
    for subpasta in SUBPASTAS_PADRAO:
        os.makedirs(os.path.join(caminho_completo, subpasta), exist_ok=True)
    return nome_pasta
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
    if "." not in (nome_arquivo or ""):
        return ""
    return nome_arquivo.rsplit(".", 1)[1].lower()
def montar_nome_padronizado(sigla, nome_cliente, data, extensao):
    return f"{sigla}_{normalizar_nome(nome_cliente)}_{data}.{extensao}"
def caminho_de_guarda(caminho_pasta_cliente, sigla):
    subpasta = SUBPASTA_POR_SIGLA.get(sigla, "06_Outros")
    destino = os.path.join(Config.PASTA_ARQUIVOS, caminho_pasta_cliente, subpasta)
    os.makedirs(destino, exist_ok=True)
    return destino, subpasta
def resolver_conflito(destino, nome_arquivo):
    if not os.path.exists(os.path.join(destino, nome_arquivo)):
        return nome_arquivo
    base, extensao = nome_arquivo.rsplit(".", 1)
    contador = 2
    while os.path.exists(os.path.join(destino, f"{base}_{contador}.{extensao}")):
        contador += 1
    return f"{base}_{contador}.{extensao}"
