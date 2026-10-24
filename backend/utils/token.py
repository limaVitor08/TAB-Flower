"""
Gera e confere o token de login.
O frontend roda numa porta e a API em outra, e usar cookie de sessão
nesse cenário complica o CORS. Por isso usamos um token assinado com a
biblioteca itsdangerous, que já vem junto com o Flask. Dentro do token
vai só o id do usuário e a validade. Como ele é assinado com a
SECRET_KEY, ninguém consegue criar ou alterar um token sem a chave.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from config import Config
# "Sal" fixo que separa este uso da chave de qualquer outro uso futuro
# da mesma SECRET_KEY (ex: recuperação de senha por link, se um dia
# existir).
_SAL = "tabflower-auth"
# Sessão dura 8 horas, um dia de trabalho no escritório. Depois disso
# a pessoa precisa logar de novo.
VALIDADE_SEGUNDOS = 8 * 60 * 60
def _serializer():
    return URLSafeTimedSerializer(Config.SECRET_KEY, salt=_SAL)
def gerar_token(usuario_id):
    """Cria um token assinado carregando o id do usuário."""
    return _serializer().dumps({"usuario_id": usuario_id})
def validar_token(token):
    """Confere assinatura e validade do token.
    Devolve o usuario_id se o token for válido, ou None se estiver
    ausente, corrompido, adulterado ou expirado.
    """
    if not token:
        return None
    try:
        dados = _serializer().loads(token, max_age=VALIDADE_SEGUNDOS)
    except (BadSignature, SignatureExpired):
        return None
    return dados.get("usuario_id")