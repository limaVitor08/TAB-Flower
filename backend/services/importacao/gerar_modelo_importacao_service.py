# Gera a planilha de exemplo para a importação
import csv
import io


class GerarModeloImportacaoService:
    @staticmethod
    def executar():
        saida = io.StringIO()
        escritor = csv.writer(saida, delimiter=";")

        escritor.writerow(
            ["nome", "tipo_pessoa", "documento", "email",
             "telefone", "endereco", "cidade", "estado", "observacao"]
        )
        escritor.writerow(
            ["Maria da Silva", "F", "529.982.247-25", "maria@exemplo.com",
             "(31) 99999-8888", "Rua das Flores, 100", "Belo Horizonte", "MG",
             "Cliente antiga, pasta fisica no armario 3"]
        )
        escritor.writerow(
            ["Silva Comercio LTDA", "J", "11.222.333/0001-81", "contato@silva.com",
             "(31) 3333-4444", "Av. Afonso Pena, 500", "Belo Horizonte", "MG", ""]
        )

        return "﻿" + saida.getvalue()
