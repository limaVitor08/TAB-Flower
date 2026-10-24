"""
Configurações do TabFlower.
As senhas e a chave secreta ficam no arquivo .env, e não aqui no código.
Assim elas não vão parar no GitHub junto com o projeto.
"""
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    """Configuração única da aplicação."""
    # Chave usada pelo Flask para assinar sessoes.
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-de-desenvolvimento")
    # --- Dados da conexão com o MySQL do WAMP ---
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "tabflower")
    # String de conexão montada para o SQLAlchemy.
    # O driver "pymysql" e quem conversa com o MySQL.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    # Desliga um recurso do SQLAlchemy que consome memória e não usamos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Pasta onde os PDFs dos clientes são gravados.
    # E a base da Funcionalidade 08 (Geração de Diretórios).
    PASTA_ARQUIVOS = os.getenv(
        "PASTA_ARQUIVOS",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "arquivos"),
    )
    # Tamanho máximo de upload: 16 MB.
    # Passando disso, o Flask recusa a requisição antes de ler o arquivo.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024