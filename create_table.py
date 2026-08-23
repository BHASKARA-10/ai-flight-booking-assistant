import sys
import os

# Add the parent directory to the Python path so we can import backend.database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db_connection

def create_table():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS saved_flights (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        airline VARCHAR(255),
        route VARCHAR(255),
        price VARCHAR(50),
        snippet TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    try:
        cursor.execute(query)
        conn.commit()
        print("Table saved_flights created successfully!")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_table()
