"""
Add novel_ids field to queries table migration script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text

def migrate():
    # Direct database URL
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'sqlite', 'metadata.db')
    engine = create_engine(f'sqlite:///{db_path}')
    
    with engine.connect() as conn:
        # Check if field exists
        result = conn.execute(text("PRAGMA table_info(queries)"))
        columns = [row[1] for row in result]
        
        if 'novel_ids' not in columns:
            conn.execute(text('ALTER TABLE queries ADD COLUMN novel_ids TEXT'))
            conn.commit()
            print('SUCCESS: Added novel_ids field to queries table')
        else:
            print('INFO: novel_ids field already exists, skipping migration')

if __name__ == '__main__':
    migrate()

