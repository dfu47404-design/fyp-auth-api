import psycopg2
import os

DATABASE_URL = "postgresql://fypuser:me9tXj1XwolsOfChIupvOU1OqZQHvwab@dpg-d4pue7c9c44c73b2ie6g-a.singapore-postgres.render.com/fypdb_jozr"

def show_structure():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # List tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    print("Tables:", cur.fetchall())

    # Show columns of users table
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users';")
    print("Users table columns:", cur.fetchall())

    cur.close()
    conn.close()

if __name__ == "__main__":
    show_structure()
