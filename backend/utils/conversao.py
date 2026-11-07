# Ajusta datas e números que voltam das stored procedures para virar JSON
from datetime import date, datetime
from decimal import Decimal
def converter_valor(valor):
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
    return [
        {chave: converter_valor(valor) for chave, valor in linha._mapping.items()}
        for linha in resultado
    ]
