# Gera e confere o token de login
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from config import Config
_SAL = "tabflower-auth"
VALIDADE_SEGUNDOS = 8 * 60 * 60
def _serializer():
    return URLSafeTimedSerializer(Config.SECRET_KEY, salt=_SAL)
def gerar_token(usuario_id):
    return _serializer().dumps({"usuario_id": usuario_id})
def validar_token(token):
    if not token:
        return None
    try:
        dados = _serializer().loads(token, max_age=VALIDADE_SEGUNDOS)
    except (BadSignature, SignatureExpired):
        return None
    return dados.get("usuario_id")
