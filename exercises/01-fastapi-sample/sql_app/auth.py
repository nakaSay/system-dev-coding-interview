from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# どのアルゴリズムを使用して電子署名を行うか
# 使用できるアルゴリズムはこちら(https://python-jose.readthedocs.io/en/latest/jws/index.html)
ALGORITHM = "HS256"

# 暗号化に使用する鍵情報
SECRET_KEY = "SECRET_KEY123"

security = HTTPBearer()

def create_tokens(user_id: int):
    """パスワード認証を行い、トークンを生成"""
    # ペイロード作成
    access_payload = {
        'exp': datetime.utcnow() + timedelta(minutes=60),
        'user_id': user_id,
    }

    # トークン作成（本来は'SECRET_KEY123'はもっと複雑にする）
    x_api_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    return x_api_token

def verify_jwt(token: str):
    try:
        """tokenからユーザーを取得"""
        # トークンをデコードしてペイロードを取得。有効期限と署名は自動で検証される。
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
    return payload

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
        )
    try:
        payload = verify_jwt(token.credentials)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed",
        )
    return payload.get('user_id')