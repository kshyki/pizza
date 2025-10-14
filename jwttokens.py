import jwt
import datetime
from fastapi import Request, HTTPException
from config import SECRET_KEY
from fastapi.responses import RedirectResponse

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'

def create_access_token(user_id: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {"sub": user_id, "type": "access", "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def access_token_required(request: Request):
    token = request.cookies.get("my_access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login", status_code=303)
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/login", status_code=303)
    if payload.get("type") != "access":
        return RedirectResponse(url="/login", status_code=303)

    return payload
