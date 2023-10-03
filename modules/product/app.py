"""
Módulo que contiene la aplicación FastAPI que maneja las rutas de producto.
"""
import datetime
import json
import os

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi import status as response_status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from lib_product.repository import (
    create_brand,
    get_brand_by_id,
    get_brand_by_name,
    get_product_exists,
    get_sku_exists,
    update_product,
)
from lib_product.schema import BrandBase, BrandReturn, ProductBase, ProductReturn
from mangum import Mangum
from sqlalchemy.orm import Session
from starlette.requests import Request

from shared_package.db import models
from shared_package.db.session import get_db
from shared_package.repository import user as user_repository
from shared_package.rol_checker import RoleChecker
from shared_package.utils import generic_post, get_data_authorizer, sqs_email, update_generic_by_model

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


@router.post("", status_code=response_status.HTTP_201_CREATED, response_model=ProductReturn)
async def product_create(
    request: Request,
    product: ProductBase,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_only_admins),
):
    """
    Create a new product in app
    """
    try:
        brand_exists = get_brand_by_id(product.brand_id, db)
        if not brand_exists:
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Brand not exists"})
        sku_exists = get_sku_exists(product.sku, db)
        if sku_exists:
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Sku already exists"}
            )
        product = product.dict(exclude_unset=True)
        product["create_by"] = data_token["user_id"]
        product["update_by"] = data_token["user_id"]
        product = models.Products(**product)
        product_db = generic_post(product, db)
        db.commit()
        return product_db
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


@router.patch("/{id}", status_code=response_status.HTTP_201_CREATED)
async def product_update(
    request: Request,
    id: int,
    product: ProductBase,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_only_admins),
):
    """
    update a product in app
    """
    try:
        product_exists = get_product_exists(id, db)
        if not product_exists:
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Product not exists"}
            )
        brand_exists = get_brand_by_id(product.brand_id, db)
        if not brand_exists:
            raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Brand not exists"})
        sku_exists = get_sku_exists(product.sku, db)
        if sku_exists and sku_exists.id != id:
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Sku already exists"}
            )
        product = product.dict(exclude_unset=True)
        product["update_by"] = data_token["user_id"]
        update_product(
            id,
            db,
            product,
        )
        db.commit()
        if float(product["price"]) != float(product_exists.price):
            users_admin = user_repository.get_users_admins(db)
            for user in users_admin:
                data = {
                    "message": f"Hi {user.full_name}, the price of the product {product_exists.name} has changed from {product_exists.price} to {product['price']}",
                    "full_name": user.full_name,
                    "type": "send_email_change_price",
                    "email": user.email,
                }
                sqs_email(json.dumps(data))
        return {
            "id": id,
            "message": "Product updated successfully",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})


@router.delete("/{id}", status_code=response_status.HTTP_201_CREATED)
async def product_delete(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    data_token=Depends(get_data_authorizer),
    auth=Depends(allow_only_admins),
):
    """
    update a product in app
    """
    try:
        product_exists = get_product_exists(id, db)
        if not product_exists:
            raise HTTPException(
                status_code=response_status.HTTP_400_BAD_REQUEST, detail={"error": "Product not exists"}
            )
        now = datetime.datetime.now()
        data_update = {
            "update_by": data_token["user_id"],
            "delete_at": now,
            "sku": f"{product_exists.sku}_deleted_{now}",
        }
        update_generic_by_model(models.Products, id, data_update, db)
        return {
            "id": id,
            "message": "Product delete successfully",
        }
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
