from fastapi import HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timezone
from fastapi.security import HTTPBearer

# В токене будет храниться
# identity - user_id
# Claims - "username":  username, "role": role

# https://37.9.53.236/

# Проверка access_token и возврат payload

http_bearer = HTTPBearer()

async def validate_token(
    token: HTTPAuthorizationCredentials,
) -> dict:
    try:
        payload = jwt.decode(token.credentials, key="", options={"verify_signature": False})
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
