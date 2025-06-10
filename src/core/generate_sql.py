#!/usr/bin/env python3
"""
Simple script to create SQL statements for uploading hospital CSV data
"""

import pandas as pd
import json
from pathlib import Path


def generate_create_table_statements():
    """Generate CREATE TABLE statements for all tables"""

    statements = []

    # Users table
    statements.append(
        """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number JSONB,
    emergency_contact JSONB,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    staff_type VARCHAR(100)
);"""
    )

    # Storage rooms table
    statements.append(
        """
CREATE TABLE IF NOT EXISTS storage_rooms (
    id INTEGER PRIMARY KEY,
    storage_number VARCHAR(50) NOT NULL,
    storage_type VARCHAR(100) NOT NULL,
    floor_number INTEGER,
    capacity INTEGER,
    notes TEXT,
);"""
    )

    # Patient records table
    statements.append(
        """
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
);"""
    )

    # Rooms table
    statements.append(
        """
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    room_number VARCHAR(50) NOT NULL,
    room_type VARCHAR(100) NOT NULL,
    bed_capacity INTEGER,
    table_count INTEGER,
    has_oxygen_outlet BOOLEAN,
    floor_number INTEGER,
    notes TEXT
);"""
    )

    # Tools table
    statements.append(
        """
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
    last_maintenance_date DATE
);"""
    )

    # Hospital inventory table
    statements.append(
        """
CREATE TABLE IF NOT EXISTS hospital_inventory (
    id INTEGER PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    item_type VARCHAR(100),
    quantity_total INTEGER,
    quantity_available INTEGER,
    location_storage_id INTEGER REFERENCES storage_rooms(id),
    location_description VARCHAR(255),
    details TEXT,
    expiry_date DATE
);"""
    )

    # Occupancy table
    statements.append(
        """
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
);"""
    )

    return statements


def main():
    print("=== SQL Statements for Hospital Database ===")
    print("\n-- CREATE TABLE STATEMENTS --")

    statements = generate_create_table_statements()
    for stmt in statements:
        print(stmt)
        print()


if __name__ == "__main__":
    main()
