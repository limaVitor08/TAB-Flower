# Confere o token antes de cada rota protegida
from flask import g, jsonify, request
from models.usuario import Usuario
from utils.token import validar_token
def carregar_usuario_da_requisicao():
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
