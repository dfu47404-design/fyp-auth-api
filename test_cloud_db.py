# show_structure.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fypuser:me9tXj1XwolsOfChIupvOU1OqZQHvwab@dpg-d4pue7c9c44c73b2ie6g-a.singapore-postgres.render.com/fypdb_jozr")

def show_structure():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        print("=" * 60)
        print("DATABASE STRUCTURE CHECK")
        print("=" * 60)
        
        # List tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
        tables = cur.fetchall()
        print(f"\n📊 Tables in database: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Show columns of users table
        print("\n👤 Users table structure:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='users' 
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        if columns:
            print(f"\n  Columns: {len(columns)}")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2]=='YES' else 'NOT NULL'} {f'DEFAULT {col[3]}' if col[3] else ''}")
        else:
            print("  ❌ Users table not found or has no columns!")
        
        # Show sample data
        print("\n📝 Sample users (first 5):")
        try:
            cur.execute("SELECT id, email, first_name, last_name, created_at FROM users LIMIT 5;")
            users = cur.fetchall()
            if users:
                for user in users:
                    print(f"  - ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}, Created: {user[4]}")
            else:
                print("  No users found in database")
        except Exception as e:
            print(f"  Could not fetch users: {e}")
        
        # Check password reset columns
        print("\n🔐 Password Reset Column Check:")
        reset_columns = ['reset_token', 'reset_token_expiry', 'is_active', 'updated_at']
        existing_columns = [col[0] for col in columns]
        
        for col in reset_columns:
            if col in existing_columns:
                print(f"  ✅ {col} exists")
            else:
                print(f"  ❌ {col} MISSING - run migrate_database.py")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database connection successful!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Database URL used: {DATABASE_URL[:50]}...")

if __name__ == "__main__":
    show_structure()