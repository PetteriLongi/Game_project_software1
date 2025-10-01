# conduit_game/db.py
import sys
import mariadb
from .config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

def get_connection():
    try:
        return mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
    except mariadb.Error as e:
        print(f"[DB] connect error: {e}")
        sys.exit(1)
