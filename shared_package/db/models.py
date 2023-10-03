from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String

from shared_package.db.base_class import Base
from shared_package.db.enums import Rol


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    email = Column(String(200), index=True, unique=True)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=False)
    rol_type = Column(Enum(Rol), default=Rol.user)
    password = Column(String(255))
    deleted_at = Column(DateTime, nullable=True, default=None)


class Brands(Base):
    __tablename__ = "brands"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    name = Column(String(200), index=True, unique=True)


class Products(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    sku = Column(String(200), index=True, unique=True)
    name = Column(String(200))
    price = Column(Float, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"))
    create_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    update_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
