import os
import time
import uuid
from datetime import timedelta

import boto3
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


def update_generic_by_model(generic_model, id, data, db: Session):
    db.query(generic_model).filter(generic_model.id == id).update(data)
    db.commit()
    return id


def sqs_email(message_body):
    print("[ Challenge - Lambda ] - START SQS EMAIL")
    try:
        if "local" == os.environ.get("ENVIRONMENT").lower() or "dev" == os.environ.get("ENVIRONMENT").lower():
            from modules.notifications.app import handler

            event = {
                "Records": [
                    {
                        "messageId": "60b76e38-1eab-4bc5-9e4c-719696ba136c",
                        "body": message_body,
                    }
                ]
            }
            handler(event)
        else:
            sqs = boto3.client(
                "sqs",
                region_name=os.environ.get("ENV_AWS_REGION"),
                aws_access_key_id=os.environ.get("ENV_AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("ENV_AWS_SECRET_ACCESS_KEY"),
            )

            queue_url = os.environ.get("SQS_NOTIFICATION_EMAIL")

            response = sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)

            print("[ Challenge - Lambda ] - END SQS EMAIL")
            return response
    except Exception as e:
        print("[ Challenge - Lambda ] - Error: {}".format(e))
        raise Exception("Exception: AWS SQS Provider {}".format(str(e)))
