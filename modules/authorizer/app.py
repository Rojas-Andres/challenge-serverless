"""
Este módulo contiene la función de controlador para autorizar y validar tokens de acceso en una función Lambda.
"""

import os
import traceback

import jwt
from lib_authorizer.utils import generate_policy, validate_token


def handler(event, context):
    """
    Función de controlador para autorizar y validar tokens de acceso en una función Lambda.

    Esta función maneja la autorización y validación de tokens de acceso en el contexto de una función Lambda.
    Verifica la presencia y validez del token de autorización en el evento proporcionado. Si el token es válido,
    genera una política de autorización con permisos adecuados y devuelve la política. Si el token no es válido
    o está ausente, genera una política que deniega el acceso.

    :param event: Los datos del evento recibido por la función Lambda.
    :type event: dict
    :param context: El contexto de la función Lambda.
    :type context: LambdaContext
    :return: Una política de autorización generada con permisos adecuados o denegando el acceso.
    :rtype: dict
    """
    try:
        print("event", event)
        print("context", context)
        if not event or not event.get("authorizationToken"):
            return generate_policy("user", "Deny")
        token = event.get("authorizationToken")
        token_decode = jwt.decode(jwt=token, key=os.getenv("SECRET_KEY"), algorithms=["HS256"])
        if not token_decode.get("uuid"):
            return generate_policy("user", "Deny")
        if "local" in os.environ.get("ENVIRONMENT").lower():
            user_id = token_decode["uuid"]
        else:
            user_id = validate_token(token_decode["uuid"])
        if user_id:
            return generate_policy(user_id, "Allow", token_decode)
        return generate_policy("user", "Deny")
    except jwt.exceptions.DecodeError:
        print(traceback.format_exc())
        return generate_policy("user", "Deny")
    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        return generate_policy("user", "Deny")
