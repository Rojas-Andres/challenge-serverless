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
from mangum import Mangum
from sqlalchemy.orm import Session
from starlette.requests import Request

from shared_package.db.session import get_db
from shared_package.repository import user as user_repository
from shared_package.repository.user import create_user
from shared_package.rol_checker import RoleChecker

# from lib_user.schema import UserBase, UserBaseAdmin, UserReturn, UserUpdate
from shared_package.schemas.user import UserBase, UserBaseAdmin, UserReturn, UserUpdate
from shared_package.utils import generic_post, get_data_authorizer, update_generic_by_model

app = FastAPI(
    debug=os.getenv("DEBUG", False),
    title="User Service",
)
allow_ony_super_admin = RoleChecker(["super_admin"])
allow_only_admins = RoleChecker(["super_admin", "admin"])

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


@router.post("/{user_id}/admin", status_code=response_status.HTTP_201_CREATED, response_model=UserReturn)
async def admin_create(
    request: Request,
    user_id,
    user: UserBaseAdmin,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_ony_super_admin),
):
    """
    Create a new admin user
    """
    try:
        user_exists = user_repository.get_user_by_email(db, user.email)
        if user_exists:
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "User already exists"}
            )
        user_db = create_user(user.dict(exclude_unset=True), db)
        return user_db
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


@router.delete("/{user_id}/admin", status_code=response_status.HTTP_200_OK)
async def admin_delete(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_ony_super_admin),
):
    """
    Create a new admin user
    """
    try:
        if user_id == str(data_token["user_id"]):
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "You can't delete yourself"}
            )
        user = user_repository.get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "User not found"})
        user_repository.delete_user(user, db)
        return {"message": "User deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


@router.patch("/{user_id}/admin", status_code=response_status.HTTP_200_OK)
async def admin_update(
    request: Request,
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_ony_super_admin),
):
    """
    Update a admin user
    """
    try:
        user = user_repository.get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "User not found"})
        user_update = user_repository.update_user(
            user_id,
            db,
            user_update.dict(exclude_unset=True),
        )
        return {"user_id": user_update, "message": "User update successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


app.include_router(router)
handler = Mangum(app)
