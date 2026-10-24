"""
Cadastra um cliente novo.
Junta três funcionalidades: valida o CPF ou CNPJ (4), bloqueia cliente
repetido (5) e cria a pasta do cliente no servidor (8).
"""
from datetime import datetime
from models.cliente import Cliente
from utils.gerenciador_arquivos import criar_estrutura_cliente
from utils.validador_documento import limpar_documento, validar_documento
class CriarClienteService:
    """Válida os dados, impede duplicidade e cria a pasta do cliente."""
    @staticmethod
    def executar(dados, criado_por=None, confirmar=True):
        """Cadastra o cliente.
        criado_por vem de g.usuario_atual, num parâmetro separado de
        "dados", que é o que o navegador enviou. Quem cadastrou não pode
        ser escolhido por quem manda a requisição.
        confirmar=False é usado pela importação em lote, que precisa gravar
        o cliente e o vínculo com o lote na mesma transação.
        """
        nome = (dados.get("nome") or "").strip()
        tipo_pessoa = (dados.get("tipo_pessoa") or "").strip().upper()
        documento = limpar_documento(dados.get("documento"))
        # --- Validacoes obrigatórias ---
        if not nome:
            raise ValueError("O nome do cliente é obrigatório.")
        if tipo_pessoa not in ("F", "J"):
            raise ValueError("O tipo de pessoa deve ser 'F' ou 'J'.")
        if not documento:
            raise ValueError("O documento é obrigatório.")
        # Funcionalidade 04
        if not validar_documento(documento, tipo_pessoa):
            rotulo = "CPF" if tipo_pessoa == "F" else "CNPJ"
            raise ValueError(f"{rotulo} inválido.")
        # Funcionalidade 05
        if Cliente.buscar_por_documento(documento):
            raise ValueError("Já existe um cliente cadastrado com este documento.")
        # Funcionalidade 08
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