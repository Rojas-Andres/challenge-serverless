"""
Este módulo contiene la clase DB, la cual se utiliza para interactuar con una base de datos DynamoDB en el contexto de
"""
import os
import time
import traceback

import boto3
import jwt


class DynamoDB:
    """
    Esta clase proporciona métodos para interactuar con la base de datos DynamoDB.
    """

    def __init__(self):
        """
        Inicializa la clase DynamoDB y establece la conexión con la base de datos DynamoDB según el entorno.
        """

        if "local" in os.environ.get("ENVIRONMENT").lower():
            self.dynamodb = boto3.resource(
                "dynamodb",
                aws_access_key_id=os.environ.get("ENV_AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("ENV_AWS_SECRET_ACCESS_KEY"),
                region_name=os.environ.get("ENV_AWS_REGION"),
            )
        else:
            self.dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")


class DB(DynamoDB):
    """
    Esta clase se utiliza para interactuar con una base de datos DynamoDB en el contexto de autenticación y generación
    de tokens.
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
        try:
            return self.auth_table.put_item(Item=data)
        except Exception as e:
            print("Error DynamoDB put_item_data: {}".format(str(e)))
            raise e

    def generate_token(self, data):
        """
        Genera un token de autenticación y almacena los datos relacionados en la base de datos.

        :param data: Los datos del token y la información asociada.
        :type data: dict
        :return: El token generado y el UUID asociado.
        :rtype: str, str
        """
        try:
            expires_at = int(time.time()) + int(os.getenv("TOKEN_EXPIRATION"))
            data["expires_at"] = expires_at
            data["uuid"] = uuid
            self.put_item_data(data)
            encode_data = jwt.encode(payload=data, key=os.getenv("SECRET_KEY"), algorithm="HS256")
            return encode_data, uuid
        except Exception as e:
            print(traceback.format_exc())
            raise Exception("Error generate_token: {}".format(str(e)))
