#!/usr/bin/env python3
"""
Hospital Database Schema Creation Script
This script only creates the database tables without importing data
"""

import psycopg2
import json
from pathlib import Path
import logging

def load_config():
    """Load configuration from JSON file"""
    config_file = Path("neon_config.json")
    if not config_file.exists():
        print("❌ ERROR: neon_config.json not found!")
        return None
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ ERROR: Failed to load configuration: {e}")
        return None

def create_connection(config):
    """Create database connection using config"""
    db_config = config['database']
    
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to database: {e}")
        return None

def get_create_table_sql():
    """Get CREATE TABLE SQL for all tables"""
    return {
        'users': """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone_number JSONB,
                emergency_contact JSONB,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                staff_type VARCHAR(100)
            );
        """,
        'storage_rooms': """
            CREATE TABLE IF NOT EXISTS storage_rooms (
                id INTEGER PRIMARY KEY,
                storage_number VARCHAR(50) NOT NULL,
                storage_type VARCHAR(100) NOT NULL,
                floor_number INTEGER,
                capacity INTEGER,
                notes TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """,
        'patient_records': """
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                date_of_birth DATE,
                gender CHAR(1),
                blood_group VARCHAR(10),
                allergies TEXT,
                medical_history TEXT,
                emergency_contact JSONB,
                contact_phone JSONB,
                date_created TIMESTAMP,
                date_updated TIMESTAMP
            );
        """,
        'rooms': """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                room_number VARCHAR(50) NOT NULL,
                room_type VARCHAR(100) NOT NULL,
                bed_capacity INTEGER,
                table_count INTEGER,
                has_oxygen_outlet BOOLEAN,
                floor_number INTEGER,
                notes TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """,
        'tools': """
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY,
                tool_name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                quantity_total INTEGER,
                quantity_available INTEGER,
                location_storage_id INTEGER REFERENCES storage_rooms(id),
                location_description VARCHAR(255),
                purchase_date DATE,
                last_maintenance_date DATE,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """,
        'hospital_inventory': """
            CREATE TABLE IF NOT EXISTS hospital_inventory (
                id INTEGER PRIMARY KEY,
                item_name VARCHAR(255) NOT NULL,
                item_type VARCHAR(100),
                quantity_total INTEGER,
                quantity_available INTEGER,
                location_storage_id INTEGER REFERENCES storage_rooms(id),
                location_description VARCHAR(255),
                last_updated TIMESTAMP,
                details TEXT,
                expiry_date DATE
            );
        """,
        'occupancy': """
            CREATE TABLE IF NOT EXISTS occupancy (
                id INTEGER PRIMARY KEY,
                room_id INTEGER REFERENCES rooms(id),
                bed_number INTEGER,
                patient_id INTEGER REFERENCES patient_records(id),
                attendee JSONB,
                assigned_at TIMESTAMP,
                discharged_at TIMESTAMP,
                tools JSONB,
                hospital_inventory JSONB,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """
    }

def create_all_tables(conn):
    """Create all tables in correct order"""
    cursor = conn.cursor()
    tables_sql = get_create_table_sql()
    
    # Create tables in dependency order
    table_order = [
        'users',
        'storage_rooms', 
        'patient_records',
        'rooms',
        'tools',
        'hospital_inventory',
        'occupancy'
    ]
    
    try:
        for table_name in table_order:
            sql = tables_sql[table_name]
            cursor.execute(sql)
            print(f"✓ Created/verified table: {table_name}")
        
        conn.commit()
        print("✅ All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main execution function"""
    print("🏥 Hospital Database Schema Creation")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    if not config:
        return False
    
    # Connect to database
    conn = create_connection(config)
    if not conn:
        return False
    
    print("✅ Connected to Neon database")
    
    try:
        # Create tables
        if create_all_tables(conn):
            print("\n🎉 Schema created successfully!")
            print("\nNext steps:")
            print("1. Use psql to connect to your Neon database")
            print("2. Use \\copy commands to import CSV data")
            print("3. Example: \\copy users FROM 'hospital_data_final/users.csv' DELIMITER ',' CSV HEADER")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()
