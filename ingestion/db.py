import os
import psycopg2


def get_connection():
    """
    Return a PostgreSQL connection to Supabase
    """
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],      
        dbname=os.environ["DB_NAME"],    
        user=os.environ["DB_USER"],      
        password=os.environ["DB_PASSWORD"],
        port=int(os.environ.get("DB_PORT", 5432)),
        sslmode="require",               
    )
    return conn
