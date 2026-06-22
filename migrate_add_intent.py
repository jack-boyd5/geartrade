#!/usr/bin/env python3
"""
Migration: Add intent column to likes table
Allows tracking whether user wants to trade or buy
"""

import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Usage: DATABASE_URL='your-db-url' python migrate_add_intent.py")
    exit(1)

def run_migration():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        print("Adding intent column to likes table...")
        
        # Add intent column (nullable for existing records)
        cursor.execute("""
            ALTER TABLE likes 
            ADD COLUMN IF NOT EXISTS intent VARCHAR(10) DEFAULT 'buy'
        """)
        
        # Set default intent to 'buy' for all existing likes
        cursor.execute("""
            UPDATE likes 
            SET intent = 'buy' 
            WHERE intent IS NULL
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - Added 'intent' column to likes table")
        print("   - Set existing likes to intent='buy'")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
