# Recebe os pedidos de usuários, perfis e troca de senha
from flask import g, jsonify, request

from services.usuario.alterar_senha_service import AlterarSenhaService
from services.usuario.atualizar_usuario_service import AtualizarUsuarioService
from services.usuario.buscar_usuario_service import BuscarUsuarioService
from services.usuario.criar_usuario_service import CriarUsuarioService
from services.usuario.excluir_usuario_service import ExcluirUsuarioService
from services.usuario.listar_perfis_service import ListarPerfisService
from services.usuario.listar_usuarios_service import ListarUsuariosService


class UsuarioController:
    @staticmethod
    def listar():
        incluir_inativos = request.args.get("incluir_inativos") == "true"
        usuarios = ListarUsuariosService.executar(
            apenas_ativos=not incluir_inativos
        )
        return jsonify([u.to_dict() for u in usuarios]), 200

    @staticmethod
    def perfis():
        perfis = ListarPerfisService.executar()
        return jsonify([p.to_dict() for p in perfis]), 200

    @staticmethod
    def buscar_por_id(id_usuario):
        try:
            usuario = BuscarUsuarioService.executar(id_usuario)
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(usuario.to_dict()), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados do usuário em JSON."}), 400

        try:
            usuario = CriarUsuarioService.executar(dados, g.usuario_atual)
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

        return jsonify(usuario.to_dict()), 201

    @staticmethod
    def atualizar(id_usuario):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Envie os dados a alterar em JSON."}), 400

        try:
            usuario = AtualizarUsuarioService.executar(
                id_usuario, dados, g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify(usuario.to_dict()), 200

    @staticmethod
    def alterar_senha(id_usuario):
        dados = request.get_json(silent=True) or {}

        try:
            AlterarSenhaService.executar(
                id_usuario, dados.get("senha"), g.usuario_atual
            )
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify({"mensagem": "Senha alterada com sucesso."}), 200

    @staticmethod
    def excluir(id_usuario):
        try:
            ExcluirUsuarioService.executar(id_usuario, g.usuario_atual)
        except PermissionError as erro:
            return jsonify({"erro": str(erro)}), 403
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

        return jsonify({"mensagem": "Usuário desativado com sucesso."}), 200
