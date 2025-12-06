import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.sql import text

print('=' * 60)
print('TESTING CLOUD DATABASE CONNECTION')
print('=' * 60)

DATABASE_URL = 'postgresql://fypuser:me9tXj1XwolsOfChIupvOU1OqZQHvwab@dpg-d4pue7c9c44c73b2ie6g-a.singapore-postgres.render.com/fypdb_jozr'

try:
    print('Connecting to Render PostgreSQL...')
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Test connection
        result = conn.execute(text('SELECT version()'))
        version = result.fetchone()[0]
        print(f'✅ Connected to PostgreSQL!')
        print(f'Version: {version[:100]}...')
        
        # Check if table exists
        result = conn.execute(text('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        '''))
        table_exists = result.fetchone()[0]
        print(f'Users table exists: {table_exists}')
        
        if not table_exists:
            print('⚠️ Users table does not exist yet. It will be created when API starts.')
        
except Exception as e:
    print(f'❌ Connection failed: {e}')
    import traceback
    traceback.print_exc()
