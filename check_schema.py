#!/usr/bin/env python3
"""
Check database schema to understand available tables and columns.
"""
import sys
sys.path.append('backend')

from backend.db_utils import db

def check_schema():
    """Check what tables and columns exist in the database."""
    try:
        # Get all tables
        tables = db.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        print("📋 Available tables in database:")
        for table in tables['table_name']:
            print(f"\n📁 {table}")
            
            # Get columns for each table
            columns = db.execute_query(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            
            for _, col in columns.iterrows():
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  - {col['column_name']} ({col['data_type']}) {nullable}")
        
        # Check sample data from first few tables
        print("\n" + "="*50)
        print("📊 Sample data from key tables:")
        
        for table in ['rooms', 'occupancy', 'users'][:3]:  # Check first 3 tables
            if table in tables['table_name'].values:
                print(f"\n🔍 Sample from {table}:")
                try:
                    sample = db.execute_query(f"SELECT * FROM {table} LIMIT 3")
                    print(sample.to_string())
                except Exception as e:
                    print(f"  Error reading {table}: {e}")
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_schema() 