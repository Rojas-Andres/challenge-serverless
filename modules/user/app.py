"""
Módulo que contiene la aplicación FastAPI que maneja las rutas de autenticación.
"""
import os

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi import status as response_status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from lib_user.schema import UserBase, UserReturn
from mangum import Mangum
from sqlalchemy.orm import Session
from starlette.requests import Request

from shared_package.db import models
from shared_package.db.session import get_db
from shared_package.utils import generic_post, get_data_authorizer

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

router = APIRouter(prefix="/user")


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


@router.post("/", status_code=response_status.HTTP_201_CREATED, response_model=UserReturn)
async def user_generic_create(request: Request, user: UserBase, db: Session = Depends(get_db)):
    try:
        user_create = models.User(**user.dict())
        user_db = generic_post(user_create, db)
        return user_db
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


@router.post("/{user_id}/admin", status_code=response_status.HTTP_201_CREATED)
async def admin_create(
    request: Request, user_id, user: UserBase, db: Session = Depends(get_db), data_token=Depends(get_data_authorizer)
):
    try:
        if not data_token.get("is_admin"):
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})
        return {"hola": "sabroso men"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


app.include_router(router)
handler = Mangum(app)