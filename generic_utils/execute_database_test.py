from os import getenv as env

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv(dotenv_path=".env")
DB_HOST_WRITER = str(env("DB_HOST_WRITER", default=""))
DB_HOST_READ = str(env("DB_HOST_READ", default=""))
DB_NAME = str(env("DB_NAME", default=""))
DB_USER = str(env("DB_USER", default=""))
DB_PASSWORD = str(env("DB_PASSWORD", default=""))
DB_PORT = str(env("DB_PORT", default=""))
DB_HOST = str(env("DB_HOST", default=""))


def close_all_connections(db_name):
    try:
        db_params = {"host": DB_HOST_WRITER, "database": db_name, "user": DB_USER, "password": DB_PASSWORD}
        conn = psycopg2.connect(host=DB_HOST_WRITER, port=DB_PORT, dbname=db_name, user=DB_USER, password=DB_PASSWORD)

        cursor = conn.cursor()

        query = sql.SQL("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = %s;")

        cursor.execute(query, [db_params["database"]])

        # Cierra el cursor y realiza cambios en la base de datos
        cursor.close()
        conn.commit()
        conn.close()

        print("Conexiones a la base de datos cerradas exitosamente.")
    except Exception as e:
        print("Error", e)


def create_database(db_name):
    try:
        conn = psycopg2.connect(host=DB_HOST_WRITER, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Base de datos '{db_name}' creada exitosamente.")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def drop_database(db_name):
    close_all_connections(db_name)
    try:
        DB_NAME = "postgres"
        conn = psycopg2.connect(host=DB_HOST_WRITER, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))

        print(f"Base de datos '{db_name}' eliminada exitosamente.")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()
