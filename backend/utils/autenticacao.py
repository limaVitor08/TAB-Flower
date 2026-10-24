"""
Confere o login antes de qualquer Controller.
Os Blueprints que exigem login registram esta função no routes.py, com
before_request. Ela lê o token do cabeçalho, busca o usuário e guarda
em g.usuario_atual. Assim os Controllers sabem quem está logado sem
confiar em nenhum id mandado pelo navegador. Sem token válido, a
resposta é 401 e o Controller nem chega a rodar.
"""
from flask import g, jsonify, request
from models.usuario import Usuario
from utils.token import validar_token
def carregar_usuario_da_requisicao():
    """Lê o header Authorization, valida o token e guarda o usuário em g.
    Se tudo estiver certo, devolve None e o Flask segue para o
    Controller normalmente. Se algo estiver errado, devolve a resposta
    de erro 401 e o Flask interrompe a requisição ali. O Controller
    nem chega a ser chamado.
    """
    # Pedido de permissão do navegador (preflight do CORS): nunca leva token.
    if request.method == "OPTIONS":
        return None
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith("Bearer "):
        return jsonify({"erro": "Faça login para continuar."}), 401
    token = cabecalho[len("Bearer "):].strip()
    usuario_id = validar_token(token)
    if not usuario_id:
        return jsonify({"erro": "Sessão expirada. Faça login novamente."}), 401
    usuario = Usuario.buscar_por_id(usuario_id)
    if not usuario or not usuario.ativo:
        return jsonify({"erro": "Usuário inválido ou inativo."}), 401
    g.usuario_atual = usuario
    return None