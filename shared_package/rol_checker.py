from fastapi import HTTPException
from starlette.requests import Request

from shared_package.utils import get_data_authorizer


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request):
        role_type = request.scope["aws.event"]["requestContext"]["authorizer"]["rol_type"]
        if role_type not in self.allowed_roles:
            raise HTTPException(status_code=403, detail={"error": "No autorizado"})
        return role_type


class RoleCheckerOptional:
    def __call__(self, request: Request):
        if (
            request.scope.get("aws.event").get("requestContext").get("authorizer").get("rol_type")
            not in self.allowed_roles
        ):
            return request.scope.get("aws.event").get("requestContext").get("authorizer").get("user_id")
        return False
