# Cadastra um cliente, confere o documento e cria a pasta dele
from datetime import datetime
from models.cliente import Cliente
from utils.gerenciador_arquivos import criar_estrutura_cliente
from utils.validador_documento import limpar_documento, validar_documento
class CriarClienteService:
    @staticmethod
    def executar(dados, criado_por=None, confirmar=True):
        nome = (dados.get("nome") or "").strip()
        tipo_pessoa = (dados.get("tipo_pessoa") or "").strip().upper()
        documento = limpar_documento(dados.get("documento"))
        if not nome:
            raise ValueError("O nome do cliente é obrigatório.")
        if tipo_pessoa not in ("F", "J"):
            raise ValueError("O tipo de pessoa deve ser 'F' ou 'J'.")
        if not documento:
            raise ValueError("O documento é obrigatório.")
        if not validar_documento(documento, tipo_pessoa):
            rotulo = "CPF" if tipo_pessoa == "F" else "CNPJ"
            raise ValueError(f"{rotulo} inválido.")
        if Cliente.buscar_por_documento(documento):
            raise ValueError("Já existe um cliente cadastrado com este documento.")
        caminho_pasta = criar_estrutura_cliente(nome, documento)
        cliente = Cliente(
            nome=nome,
            tipo_pessoa=tipo_pessoa,
            documento=documento,
            email=(dados.get("email") or "").strip() or None,
            telefone=(dados.get("telefone") or "").strip() or None,
            endereco=(dados.get("endereco") or "").strip() or None,
            cidade=(dados.get("cidade") or "").strip() or None,
            estado=(dados.get("estado") or "").strip().upper() or None,
            observacao=(dados.get("observacao") or "").strip() or None,
            caminho_pasta=caminho_pasta,
            criado_por=criado_por,
            criado_em=datetime.now(),
            ativo=True,
        )
        return cliente.salvar(confirmar=confirmar)
