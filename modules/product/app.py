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
from lib_product.repository import create_brand, get_brand_by_name
from lib_product.schema import BrandBase, BrandReturn, ProductBase, ProductReturn
from mangum import Mangum
from sqlalchemy.orm import Session
from starlette.requests import Request

from shared_package.db.session import get_db
from shared_package.rol_checker import RoleChecker
from shared_package.utils import generic_post, get_data_authorizer, update_generic_by_model

app = FastAPI(
    debug=os.getenv("DEBUG", False),
    title="User Service",
)
allow_only_admins = RoleChecker(["super_admin", "admin"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter(prefix="/product")


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


@router.post("/", status_code=response_status.HTTP_201_CREATED, response_model=ProductReturn)
async def product_create(
    request: Request,
    product: ProductBase,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_only_admins),
):
    """
    Create a new user in app
    """
    try:
        return {"hola": "asdasdas"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


@router.post("/brand", status_code=response_status.HTTP_201_CREATED, response_model=BrandReturn)
async def brand_create(
    request: Request,
    brand: BrandBase,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_only_admins),
):
    """
    Create a brand
    """
    try:
        brand_exists = get_brand_by_name(brand.name, db)
        if brand_exists:
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Brand already exists"}
            )
        brand_db = create_brand(brand.dict(exclude_unset=True), db)
        return brand_db
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


app.include_router(router)
handler = Mangum(app)
