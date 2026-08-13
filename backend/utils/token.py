"""
Geração e validação do token de sessão.

Porque essa abordagem: o projeto usa Flask + frontend em porta separada
(Live Server), então sessão de cookie do Flask complicaria o CORS sem
necessidade. Em vez disso usamos um token assinado (itsdangerous, que já
vem instalado junto com o Flask - nenhuma biblioteca nova precisa ir no
requirements.txt).

O token carrega só o id do usuário e uma validade. Ele é assinado com a
SECRET_KEY da aplicação: ninguém consegue forjar um token sem conhecer
essa chave, e qualquer alteração no conteúdo invalida a assinatura.

Isso NÃO é JWT (não tem padrão de biblioteca externa nem cabeçalho
próprio) - é a forma mais simples que resolve o problema: usuario_id
não pode mais vir "no que o frontend disser", ele vem do token.
"""

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import Config

# "Sal" fixo que separa este uso da chave de qualquer outro uso futuro
# da mesma SECRET_KEY (ex: recuperação de senha por link, se um dia
# existir). Não é segredo, só evita colisão de propósito.
_SAL = "tabflower-auth"

# Sessão dura 8 horas - um dia de trabalho no escritório. Depois disso
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
