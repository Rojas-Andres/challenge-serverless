from sqlalchemy.orm import Session

from shared_package.db import models
from shared_package.utils import generic_post


def get_brand_by_name(name, db: Session):
    user_exists = (
        db.query(
            models.Brands.id,
            models.Brands.name,
        )
        .filter(models.Brands.name == name)
        .first()
    )
    return user_exists


def create_brand(user, db: Session):
    brand = models.Brands(**user)
    breand_db = generic_post(brand, db)
    return breand_db
