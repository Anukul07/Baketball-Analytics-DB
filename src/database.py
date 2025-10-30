import os
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """
    Connects to the PostgreSQL database using credentials from .env
    """ 
    load_dotenv(dotenv_path='../.env') 
    
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("✅ Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def init_database():
    """
    Initializes the database by running the schema.sql file.
    This will create all the necessary tables.
    """
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to database. Aborting initialization.")
        return

    try:
        with conn.cursor() as cursor:
            with open('../sql/schema.sql', 'r') as f:
                sql_script = f.read()
            cursor.execute(sql_script)
            conn.commit()
            print("✅ Database tables created successfully from schema.sql.")

    except (psycopg2.Error, IOError) as e:
        print(f"Error initializing database: {e}")
        conn.rollback()

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Running database initialization...")
    init_database()