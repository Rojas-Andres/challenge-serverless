"""
Este módulo contiene la clase DB, la cual se utiliza para interactuar con una base de datos DynamoDB en el contexto de
"""
import json
import os
import time
import traceback

import jwt
from lib_authorizer.dynamoDB import DynamoDB

# from shared_package.utils import generateUniqueID


class DB(DynamoDB):
    """
    Clase que proporciona métodos para interactuar con una base de datos DynamoDB en el contexto de tokens de
    autorización.
    """

    def __init__(self):
        """
        Inicializa la clase DB y establece la conexión con la base de datos DynamoDB.
        """
        super().__init__()

        self.auth_table = self.dynamodb.Table(os.getenv("AUTHORIZER_TABLE"))

    def get_item_by_token(self, uuid):
        """
        Obtiene un elemento de la tabla por su UUID.

        :param uuid: El UUID del elemento que se va a buscar.
        :type uuid: str
        :return: El ID de usuario asociado al UUID si se encuentra, de lo contrario, None.
        :rtype: str or None
        """
        try:
            token_exist = self.auth_table.get_item(Key={"uuid": uuid}).get("Item")
            return token_exist.get("user_id") if token_exist else None
        except Exception as e:
            print("Error DynamoDB get_item_by_token: {}".format(str(e)))
            return None

    def put_item_data(self, data):
        """
        Inserta un nuevo elemento en la tabla.

        :param data: Los datos del elemento que se va a insertar.
        :type data: dict
        :return: El resultado de la operación de inserción.
        """
        return self.auth_table.put_item(Item=data)

    def generate_token(self, data):
        """
        Genera un token de autorización y almacena los datos relacionados en la base de datos.

        :param data: Los datos del token y la información asociada.
        :type data: dict
        :return: El token generado y el UUID asociado.
        :rtype: str, str
        :raises Exception: Si ocurre un error al generar el token.
        """
        try:
            uuid = "123451"
            expires_at = int(time.time()) + int(os.getenv("TOKEN_EXPIRATION"))
            data["expires_at"] = expires_at
            data["uuid"] = uuid
            data["organizations"] = json.dumps(data["organizations"], separators=(",", ":"))
            self.put_item_data(data)
            encode_data = jwt.encode(payload=data, key=os.getenv("SECRET_KEY"), algorithm="HS256")
            return encode_data, uuid
        except Exception:
            print(traceback.format_exc())
            raise Exception("Error while generating token")
