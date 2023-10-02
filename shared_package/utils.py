import os
from datetime import timedelta

import jwt
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.requests import Request


def generic_post(data, db: Session):
    db = db.using_bind("writer")
    db.add(data)
    db.commit()
    return data


def get_data_authorizer(request: Request):
    if "local" in os.environ.get("ENVIRONMENT").lower() or "dev" in os.environ.get("ENVIRONMENT").lower():
        token = request.headers.get("Authorization")
        try:
            token_decode = jwt.decode(jwt=token, key=os.getenv("SECRET_KEY"), algorithms=["HS256"])
        except Exception:
            raise HTTPException(status_code=401, detail="You are not permission")
        try:
            request.scope["aws.event"] = {
                "requestContext": {
                    "authorizer": {
                        "user_id": token_decode.get("user_id"),
                        "is_admin": token_decode.get("is_admin"),
                    }
                }
            }
        except Exception:
            raise HTTPException(status_code=401, detail="You are not permission")
        return token_decode
    context = request.scope["aws.event"]["requestContext"]["authorizer"]
    return context
