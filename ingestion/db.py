import psycopg2
from config import settings


def get_connection():
    """
    Return a PostgreSQL connection using settings from the configuration.
    """
    if settings.DATABASE_URL:
        conn = psycopg2.connect(settings.DATABASE_URL)
    else:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT,
        )
    conn.autocommit = False
    return conn