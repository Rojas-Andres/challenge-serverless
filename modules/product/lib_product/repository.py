"""
Repository for product module
"""
from sqlalchemy.orm import Session

from shared_package.db import models
from shared_package.utils import generic_post


def get_brand_by_name(name, db: Session):
    """
    Get brand by name
    """
    brand_exists = (
        db.query(
            models.Brands.id,
            models.Brands.name,
        )
        .filter(models.Brands.name == name)
        .first()
    )
    return brand_exists


def get_brand_by_id(id, db: Session):
    """
    Get brand by id
    """
    brand_exists = (
        db.query(
            models.Brands.id,
            models.Brands.name,
        )
        .filter(models.Brands.id == id)
        .first()
    )
    return brand_exists


def get_product_exists(id, db: Session):
    """
    Get product by id
    """
    product_exists = (
        db.query(models.Products.id, models.Products.name, models.Products.price, models.Products.sku)
        .filter(models.Products.id == id, models.Products.delete_at.is_(None))
        .first()
    )
    return product_exists


def get_sku_exists(sku_id, db: Session):
    """
    Get sku exists
    """
    sku_exists = (
        db.query(
            models.Products.id,
            models.Products.name,
        )
        .filter(models.Products.sku == sku_id)
        .first()
    )
    return sku_exists


def update_product(id: int, db: Session, data: dict):
    db.query(models.Products).filter(models.Products.id == id).update(data)
    db.commit()
    return id


def create_brand(user, db: Session):
    """
    Create a brand
    """
    brand = models.Brands(**user)
    breand_db = generic_post(brand, db)
    return breand_db


def create_product(user, db: Session):
    """
    Create a product
    """
    product = models.Products(**user)
    breand_db = generic_post(product, db)
    return breand_db


def delete_product(product, db: Session):
    pass
