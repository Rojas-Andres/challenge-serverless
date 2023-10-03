import enum


class Rol(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    user = "user"
