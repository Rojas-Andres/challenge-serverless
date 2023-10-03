"""
Módulo que proporciona métodos para interactuar con la base de datos DynamoDB.
"""
import os
from functools import reduce
from operator import and_

import boto3
from boto3.dynamodb.conditions import Attr


class DynamoDB:
    """
    Clase que proporciona métodos para interactuar con la base de datos DynamoDB.
    """

    def __init__(self):
        """
        Inicializa la clase DynamoDB y establece la conexión con la base de datos DynamoDB según el entorno.
        """
        if "local" in os.environ.get("ENVIRONMENT").lower():
            self.dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
        else:
            self.dynamodb = boto3.resource(
                "dynamodb",
                aws_access_key_id=os.environ.get("ENV_AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("ENV_AWS_SECRET_ACCESS_KEY"),
                region_name=os.environ.get("ENV_AWS_REGION"),
            )

    def build_query_params(self, filters):
        """
        Construye los parámetros de consulta basados en los filtros proporcionados.

        :param filters: Los filtros para la consulta.
        :type filters: dict
        :return: Los parámetros de consulta construidos.
        :rtype: dict
        """
        query_params = {}
        if len(filters) > 0:
            query_params["FilterExpression"] = self.add_expressions(filters)
        return query_params

    def add_expressions(self, filters: dict):
        """
        Construye expresiones de filtro para la consulta.

        :param filters: Los filtros para la consulta.
        :type filters: dict
        :return: La expresión de filtro construida.
        :rtype: Attr or None
        """
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, int):
                    conditions.append(Attr(key).eq(value))
            return reduce(and_, conditions)
        return None
