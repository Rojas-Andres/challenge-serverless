"""
Function to test auth
"""
import os

# from shared_package.hashing import Hasher as Hash
# from shared_package.load_test_fixture import generate_fake_data_by_model
import uuid
from unittest import TestCase

import bcrypt
import boto3
from faker import Faker
from moto import mock_dynamodb
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from generic_utils.execute_database_test import create_database, drop_database
from shared_package.db.models import Base, User
from shared_package.repository.user import create_user
from shared_package.utils import generate_token, get_data_authorizer

fake = Faker()


def create_models_database(database_name: str):
    """
    Crea los modelos de la base de datos.
    """
    SQLALCHEMY_DATABASE_URL_READ = "postgresql://{}:{}@{}:{}/{}".format(
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST_READ"),
        os.getenv("DB_PORT"),
        database_name,
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL_READ, echo=False)
    Base.metadata.create_all(bind=engine)


def create_session():
    sql_database_url = "postgresql://{}:{}@{}:{}/{}".format(
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST_WRITER"),
        os.getenv("DB_PORT"),
        os.getenv("DB_NAME"),
    )
    engine = create_engine(sql_database_url, logging_name="reader", echo=False)
    sesion_local = sessionmaker(autocommit=False, bind=engine)
    return sesion_local()


def create_user_test(data, db: Session):
    data["password"] = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(**data)
    db.add(user)
    db.commit()
    return data


class TestUser(TestCase):
    """
    Clase para probar la autenticación.
    """

    @classmethod
    def setUpClass(cls):
        """
        Inicializa la base de datos de dynamo y la base de datos de postgres.
        """
        name_database = "test_database_user"
        mocking = mock_dynamodb()
        mocking.start()
        dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
        try:
            dynamodb.create_table(
                TableName=os.environ.get("AUTHORIZER_TABLE"),
                KeySchema=[{"AttributeName": "uuid", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "uuid", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
        except Exception as e:
            print("Error create_table_auth: {}".format(e))
        drop_database(name_database)
        create_database(name_database)
        create_models_database(name_database)
        os.environ["DB_NAME"] = name_database

    def setUp(self):
        """
        Inicializa el cliente para realizar las pruebas.
        """

        self.session = create_session()
        super().setUp()
        self.data = {
            "full_name": "",
            "password": "asddsadsadsadsasda",
            "email": "useraa1@example.com",
        }
        from user.app import app

        with TestClient(app) as client:
            self.client = client

    def test_admin_create_bad(self):
        """
        Test crear usuario admin , pero no envia el token
        """
        response = self.client.post(
            "/user/7/admin",
            json=self.data,
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "You are not permission"

    def test_admin_create_user_bad_permission(self):
        """
        Test crear usuario admin , pero no envia el token
        """
        self.data["rol_type"] = "admin"
        token = generate_token(self.data)
        response = self.client.post("/user/7/admin", json=self.data, headers={"Authorization": token})
        assert response.status_code == 403
        assert response.json()["detail"]["error"] == "No autorizado"

    def test_admin_create_user_create_good(self):
        """
        Test crear usuario admin , pero no envia el token
        """
        self.data["rol_type"] = "super_admin"
        self.data["email"] = fake.email()
        token = generate_token(self.data)
        response = self.client.post("/user/7/admin", json=self.data, headers={"Authorization": token})
        assert response.status_code == 201
        assert response.json()["email"] == self.data["email"]

    def test_admin_create_user_aleady_exists(self):
        """
        Test crear usuario admin , pero no envia el token
        """
        self.data["rol_type"] = "super_admin"
        self.data["email"] = "andres@gmail.com"
        token = generate_token(self.data)
        response = self.client.post("/user/7/admin", json=self.data, headers={"Authorization": token})
        assert response.status_code == 201
        assert response.json()["email"] == self.data["email"]
        response = self.client.post("/user/7/admin", json=self.data, headers={"Authorization": token})
        assert response.status_code == 400
        assert response.json()["detail"]["error"] == "User already exists"
