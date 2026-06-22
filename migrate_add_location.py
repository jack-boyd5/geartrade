"""
Migration: Add latitude/longitude to users table
Run once on production database
"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = input("Enter DATABASE_URL: ")

def migrate():
    print("🔧 Running migration: Add lat/lng to users...")
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    
    try:
        # Add columns if they don't exist
        c.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS latitude FLOAT,
            ADD COLUMN IF NOT EXISTS longitude FLOAT
        """)
        conn.commit()
        print("✅ Migration complete!")
        print("   - Added latitude column")
        print("   - Added longitude column")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
