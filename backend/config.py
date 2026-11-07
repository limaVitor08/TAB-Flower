# Lê as configurações do .env, como a chave secreta e os dados do banco
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-de-desenvolvimento")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "tabflower")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PASTA_ARQUIVOS = os.getenv(
        "PASTA_ARQUIVOS",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "arquivos"),
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
