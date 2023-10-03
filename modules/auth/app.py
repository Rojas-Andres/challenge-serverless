"""
Módulo que contiene la aplicación FastAPI que maneja las rutas de autenticación.
"""
import os

import bcrypt
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi import status as response_status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from lib_auth.schema import AuthReturn, Credentials
from mangum import Mangum
from sqlalchemy.orm import Session
from starlette.requests import Request

from shared_package.db import models
from shared_package.db.session import get_db
from shared_package.repository import user as user_repository
from shared_package.utils import get_data_authorizer, get_user_data

app = FastAPI(
    debug=os.getenv("DEBUG", False),
    title="User Service",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/auth")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Maneja las excepciones de validación que ocurren al procesar una solicitud HTTP en FastAPI.

    :param request: La solicitud HTTP que causó la excepción.
    :type request: Request
    :param exc: La excepción de validación que fue capturada.
    :type exc: RequestValidationError
    :return: Una respuesta JSON que describe los errores de validación y el contenido de la solicitud.
    :rtype: JSONResponse
    """
    return JSONResponse(
        status_code=response_status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"errors": exc.errors(), "body": exc.body}),
    )


@router.post("/", status_code=response_status.HTTP_200_OK, response_model=AuthReturn)
async def singin(request: Request, credentials: Credentials, db: Session = Depends(get_db)):
    try:
        user = user_repository.get_user_by_email(db, credentials.email)
        if not user:
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "User not found"})
        validate_password = bcrypt.checkpw(credentials.password.encode("utf-8"), user.password.encode("utf-8"))
        if not validate_password:
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Invalid password"})
        data_token = get_user_data(user)
        return data_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


app.include_router(router)
handler = Mangum(app)
