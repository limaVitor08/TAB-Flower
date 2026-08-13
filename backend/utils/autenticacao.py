"""
Middleware de autenticação.

Camada de Infraestrutura, ao lado de extensions.py. Não é Model, não é
Service, não é Controller: é uma checagem que roda ANTES do Controller,
para todas as rotas que exigem login.

Como se liga: cada Blueprint que exige login registra esta função com
`meu_blueprint.before_request(carregar_usuario_da_requisicao)`, feito
uma vez em routes.py. As rotas de login e de status ficam de fora e
continuam públicas.

O usuário autenticado fica disponível durante a requisição inteira em
`flask.g.usuario_atual` - qualquer Controller pode ler `g.usuario_atual`
sem precisar confiar em nada que veio do corpo ou da URL da requisição.
Isso fecha a brecha que existia antes: qualquer requisição podia dizer
"eu sou o usuário X" simplesmente mandando `usuario_id=X`.
"""

from flask import g, jsonify, request

from models.usuario import Usuario
from utils.token import validar_token


def carregar_usuario_da_requisicao():
    """Lê o header Authorization, valida o token e guarda o usuário em g.

    Se tudo estiver certo, devolve None e o Flask segue para o
    Controller normalmente. Se algo estiver errado, devolve a resposta
    de erro 401 e o Flask interrompe a requisição ali - o Controller
    nem chega a ser chamado.
    """
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
