import os
from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://fypuser:me9tXj1XwolsOfChIupvOU1OqZQHvwab@dpg-d4pue7c9c44c73b2ie6g-a.singapore-postgres.render.com/fypdb_jozr'

engine = create_engine(DATABASE_URL)

print('=' * 60)
print('CHECKING DATABASE')
print('=' * 60)

with engine.connect() as conn:
    # Check tables
    result = conn.execute(text('''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    '''))
    
    tables = result.fetchall()
    print(f'Total tables: {len(tables)}')
    
    for table in tables:
        print(f'  📊 Table: {table[0]}')
        
        # Count rows
        count_result = conn.execute(text(f'SELECT COUNT(*) FROM {table[0]}'))
        count = count_result.fetchone()[0]
        print(f'    Rows: {count}')
        
        # Show first few rows
        if count > 0:
            data_result = conn.execute(text(f'SELECT * FROM {table[0]} LIMIT 3'))
            rows = data_result.fetchall()
            print('    Sample data:')
            for row in rows:
                print(f'      {row}')
    
    print('=' * 60)
