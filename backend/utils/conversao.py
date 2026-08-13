"""
Conversão das linhas devolvidas pelas stored procedures.

As Models controlam o próprio to_dict() e formatam cada campo. Já as
procedures devolvem linhas cruas, com tipos do banco: DATE, DATETIME e
DECIMAL viram objetos Python que o Flask serializa de um jeito diferente
do resto da API.

Um DATE, por exemplo, sairia como "Sat, 15 Aug 2026 00:00:00 GMT" em vez
de "2026-08-15", e o JavaScript da tela não saberia ler.

Normalizar aqui, na fronteira entre o banco e a aplicação, mantem toda a
API falando o mesmo formato.
"""

from datetime import date, datetime
from decimal import Decimal


def converter_valor(valor):
    """Converte um valor do banco para algo que vira JSON limpo."""
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (bytes, bytearray)):
        return valor.decode("utf-8", errors="ignore")
    return valor


def converter_linhas(resultado):
    """Transforma o retorno de uma procedure em lista de dicionarios."""
    return [
        {chave: converter_valor(valor) for chave, valor in linha._mapping.items()}
        for linha in resultado
    ]
