"""
Arruma as linhas que voltam das stored procedures antes de virar JSON.
As Models têm o próprio to_dict(), mas as procedures devolvem os dados
crus do banco. Sem esta conversão, uma data sairia como
"Sat, 15 Aug 2026 00:00:00 GMT" em vez de "2026-08-15", e o JavaScript
da tela não ia entender.
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