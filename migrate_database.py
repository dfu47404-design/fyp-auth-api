# migrate_database.py - FIXED FOR SQLALCHEMY 2.0
from app.db import engine
from app.models import Base
import sqlalchemy as sa

print('=' * 60)
print('DATABASE MIGRATION FOR PASSWORD RESET')
print('=' * 60)

try:
    # First, let's check current columns
    with engine.begin() as conn:  # Use engine.begin() for auto-commit
        inspector = sa.inspect(engine)
        
        # Check if users table exists
        if not inspector.has_table('users'):
            print("❌ Users table doesn't exist. Creating from scratch...")
            Base.metadata.create_all(bind=engine)
            print("✅ Users table created successfully!")
        else:
            # Check existing columns
            columns = inspector.get_columns('users')
            column_names = [c['name'] for c in columns]
            print(f"Current columns in 'users' table: {column_names}")
            
            # Check for missing columns for password reset
            required_columns = ['reset_token', 'reset_token_expiry', 'is_active', 'updated_at']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"Missing columns: {missing_columns}")
                
                # Add missing columns one by one
                if 'reset_token' not in column_names:
                    print("Adding 'reset_token' column...")
                    conn.execute(sa.text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)"))
                    print("✅ Added 'reset_token' column")
                
                if 'reset_token_expiry' not in column_names:
                    print("Adding 'reset_token_expiry' column...")
                    conn.execute(sa.text("ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP"))
                    print("✅ Added 'reset_token_expiry' column")
                
                if 'is_active' not in column_names:
                    print("Adding 'is_active' column...")
                    conn.execute(sa.text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true"))
                    print("✅ Added 'is_active' column")
                
                if 'updated_at' not in column_names:
                    print("Adding 'updated_at' column...")
                    conn.execute(sa.text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE"))
                    print("✅ Added 'updated_at' column")
                
                print("\n✅ Migration completed successfully!")
                print(f"✅ Added {len(missing_columns)} columns to users table")
            else:
                print("✅ All required columns already exist!")
    
    print('=' * 60)
    print("✅ Database migration completed!")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()