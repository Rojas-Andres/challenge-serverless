from sqlalchemy.orm import Session

from shared_package.db import models
from shared_package.utils import generic_post


def create_user(user, db: Session):
    user_create = models.User(**user)
    user_db = generic_post(user_create, db)
    return user_db
