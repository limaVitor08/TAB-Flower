"""
Validação de CPF e CNPJ.

Funcionalidade 04 (Validação de Documento).

Estas funções conferem os digitos verificadores, ou seja, confirmam que o
número e matematicamente válido. Elas Não consultam a Receita Federal,
entao não garantem que o documento exista de verdade.
"""


def limpar_documento(documento):
    """Remove pontos, tracos, barras e espacos, deixando só os números."""
    if not documento:
        return ""
    return "".join(caractere for caractere in str(documento) if caractere.isdigit())


def validar_cpf(cpf):
    """Confere os dois digitos verificadores do CPF."""
    cpf = limpar_documento(cpf)

    if len(cpf) != 11:
        return False

    # Sequencias como 111.111.111-11 passam no calculo, mas não existem.
    if cpf == cpf[0] * 11:
        return False

    # Primeiro digito: pesos de 10 a 2 sobre os 9 primeiros números.
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    primeiro_digito = (soma * 10) % 11
    if primeiro_digito == 10:
        primeiro_digito = 0
    if primeiro_digito != int(cpf[9]):
        return False

    # Segundo digito: pesos de 11 a 2 sobre os 10 primeiros números.
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    segundo_digito = (soma * 10) % 11
    if segundo_digito == 10:
        segundo_digito = 0

    return segundo_digito == int(cpf[10])


def validar_cnpj(cnpj):
    """Confere os dois digitos verificadores do CNPJ."""
    cnpj = limpar_documento(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = sum(int(cnpj[i]) * pesos_primeiro[i] for i in range(12))
    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto
    if primeiro_digito != int(cnpj[12]):
        return False

    soma = sum(int(cnpj[i]) * pesos_segundo[i] for i in range(13))
    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto

    return segundo_digito == int(cnpj[13])


def validar_documento(documento, tipo_pessoa):
    """Válida o documento de acordo com o tipo de pessoa.

    tipo_pessoa: 'F' para pessoa física (CPF), 'J' para jurídica (CNPJ).
    """
    if tipo_pessoa == "F":
        return validar_cpf(documento)
    if tipo_pessoa == "J":
        return validar_cnpj(documento)
    return False


def formatar_documento(documento, tipo_pessoa):
    """Devolve o documento pontuado, para exibicao na tela.

    CPF  -> 000.000.000-00
    CNPJ -> 00.000.000/0000-00
    """
    d = limpar_documento(documento)

    if tipo_pessoa == "F" and len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"

    if tipo_pessoa == "J" and len(d) == 14:
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"

    return d
