# conduit_game/db.py
from .config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    return connection
