from sqlalchemy.orm import Session

from shared_package.db import models


def get_user_by_email(db: Session, email):
    user_exists = (
        db.query(
            models.User.id,
            models.User.full_name,
            models.User.is_super_admin,
            models.User.is_admin,
            models.User.password,
            models.User.id.label("user_id"),
        )
        .filter(models.User.email == email)
        .first()
    )
    return user_exists
