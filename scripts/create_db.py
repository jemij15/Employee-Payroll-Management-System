"""
Utility script to create the 'payroll_db' PostgreSQL database if it does not exist.
Reads connection credentials directly from the .env file.
"""
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def create_database():
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    try:
        # Connect to default 'postgres' database to check/create target database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating it now...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}";')
            print(f"Database '{DB_NAME}' created successfully!")
        else:
            print(f"Database '{DB_NAME}' already exists. No action needed.")

        cursor.close()
        conn.close()

        # Now test table creation safely
        print("Safely creating tables using SQLAlchemy models...")
        from app.database import init_db
        init_db()
        print("All tables ('employees', 'payrolls') are ready!")

    except psycopg2.OperationalError as e:
        print("\n[ERROR] Could not connect to PostgreSQL server.")
        print("Please ensure:")
        print("1. PostgreSQL is installed and the service is running.")
        print("2. Your DB_PASSWORD in the '.env' file is correct.")
        print(f"\nDetails: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()
