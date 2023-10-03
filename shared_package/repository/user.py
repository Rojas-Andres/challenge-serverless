from sqlalchemy.orm import Session

from shared_package.db import models
from shared_package.utils import generic_post


def get_user_by_email(db: Session, email):
    user_exists = (
        db.query(
            models.User.id,
            models.User.full_name,
            models.User.rol_type,
            models.User.password,
            models.User.id.label("user_id"),
        )
        .filter(models.User.email == email)
        .first()
    )
    return user_exists


def get_user_by_id(db: Session, id):
    user_exists = (
        db.query(
            models.User.id,
            models.User.full_name,
            models.User.rol_type,
            models.User.password,
            models.User.id.label("user_id"),
        )
        .filter(models.User.id == id)
        .first()
    )
    return user_exists


def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


def delete_user(user: models.User, db: Session):
    db.delete(user)
    db.commit()
    return user


def update_user(user_id: int, db: Session, data: dict):
    db.query(models.User).filter(models.User.id == user_id).update(data)
    db.commit()
    return user_id


def create_user(user, db: Session):
    user_create = models.User(**user)
    user_db = generic_post(user_create, db)
    return user_db
