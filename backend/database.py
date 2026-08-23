import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3307")),
            database=os.getenv("DB_NAME", "flight_booking_assistant"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def init_db():
    """
    Initializes the database using the schema.sql file.
    Only run this once during setup.
    """
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # You would read the schema.sql and execute it here if needed,
            # but usually, you run schema.sql directly in XAMPP phpMyAdmin or MySQL CLI.
            print("Database connection successful.")
        except Error as e:
            print(f"Error initializing DB: {e}")
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_db()
