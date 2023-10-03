import os
import time
import uuid
from datetime import timedelta

import jwt
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.requests import Request

from shared_package.dynamo_db import DB


def generic_post(data, db: Session):
    """
    Generic post data
    """
    db = db.using_bind("writer")
    db.add(data)
    db.commit()
    return data


def get_data_authorizer(request: Request):
    """
    Get data authorizer
    """
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
                        "rol_type": token_decode.get("rol_type"),
                    }
                }
            }
        except Exception:
            raise HTTPException(status_code=401, detail="You are not permission")
        return token_decode
    context = request.scope["aws.event"]["requestContext"]["authorizer"]
    return context


def generate_token(data):
    expires_at = int(time.time()) + int(os.getenv("TOKEN_EXPIRATION"))
    data["expires_at"] = expires_at
    data["uuid"] = generate_unique_id()
    encode_data = jwt.encode(payload=data, key=os.getenv("SECRET_KEY"), algorithm="HS256")
    return encode_data


def get_user_data(user):
    """
    Get user data and generate token
    """
    if user:
        # database_dynamo = DB()
        user_data = user._asdict()
        token = generate_token(user_data)
        return {"access_token": token, **user_data}


def generate_unique_id():
    return str(uuid.uuid4())
