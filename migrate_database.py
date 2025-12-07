from app.db import engine
import sqlalchemy as sa

with engine.connect() as conn:
    inspector = sa.inspect(engine)
    columns = inspector.get_columns('users')
    names = [c['name'] for c in columns]

    if 'reset_token' not in names:
        conn.execute(sa.text("""
            ALTER TABLE users 
            ADD COLUMN reset_token VARCHAR(255),
            ADD COLUMN reset_token_expiry TIMESTAMP,
            ADD COLUMN is_active BOOLEAN DEFAULT true;
        """))
        print("Migration complete ✅")
    else:
        print("Columns already exist ✅")
