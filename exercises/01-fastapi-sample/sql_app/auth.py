from jose import jwt
from datetime import datetime, timedelta

# どのアルゴリズムを使用して電子署名を行うか
# 使用できるアルゴリズムはこちら(https://python-jose.readthedocs.io/en/latest/jws/index.html)
ALGORITHM = "HS256"

# 暗号化に使用する鍵情報
SECRET_KEY = "SECRET_KEY123"

def create_tokens(user_id: int):
    """パスワード認証を行い、トークンを生成"""
    # ペイロード作成
    access_payload = {
        'token_type': 'x_api_token',
        'exp': datetime.utcnow() + timedelta(minutes=60),
        'user_id': user_id,
    }

    # トークン作成（本来は'SECRET_KEY123'はもっと複雑にする）
    x_api_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {'x_api_token': x_api_token, 'token_type': 'bearer'}
