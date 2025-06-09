"""
Mock data generator for Smart Hospital Analytics.
Provides realistic test data when database is not available.
"""
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import random


def generate_mock_rooms():
    """Generate mock rooms data."""
    rooms_data = [
        {"id": 1, "room_type": "ICU", "bed_capacity": 2, "status": "active"},
        {"id": 2, "room_type": "ICU", "bed_capacity": 2, "status": "active"},
        {"id": 3, "room_type": "ICU", "bed_capacity": 1, "status": "active"},
        {"id": 4, "room_type": "Emergency", "bed_capacity": 4, "status": "active"},
        {"id": 5, "room_type": "Emergency", "bed_capacity": 4, "status": "active"},
        {"id": 6, "room_type": "Emergency", "bed_capacity": 3, "status": "active"},
        {"id": 7, "room_type": "General Ward", "bed_capacity": 6, "status": "active"},
        {"id": 8, "room_type": "General Ward", "bed_capacity": 6, "status": "active"},
        {"id": 9, "room_type": "General Ward", "bed_capacity": 4, "status": "active"},
        {"id": 10, "room_type": "Surgical", "bed_capacity": 3, "status": "active"},
        {"id": 11, "room_type": "Surgical", "bed_capacity": 3, "status": "active"},
        {"id": 12, "room_type": "Pediatric", "bed_capacity": 4, "status": "active"},
    ]
    return pd.DataFrame(rooms_data)


def generate_mock_occupancy(days_back=90):
    """Generate mock occupancy data."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    occupancy_data = []
    
    # Generate realistic occupancy patterns
    for i in range(200):  # 200 patient stays
        room_id = random.randint(1, 12)
        patient_id = 1000 + i
        
        # Random admission time within the period
        admission_days_ago = random.randint(1, days_back)
        assigned_at = end_date - timedelta(days=admission_days_ago)
        
        # Add some time of day variation
        assigned_at += timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Generate discharge time (some patients still admitted)
        if random.random() < 0.3:  # 30% still in hospital
            discharged_at = None
        else:
            los_days = np.random.exponential(3.5)  # Average 3.5 day stay
            discharged_at = assigned_at + timedelta(days=los_days)
            if discharged_at > end_date:  # Don't discharge in future
                discharged_at = None
        
        attendee = random.choice(["Dr. Smith", "Dr. Johnson", "Dr. Brown", "Dr. Davis", "Dr. Wilson"])
        age_at_adm = random.randint(18, 85)
        gender = random.choice(["M", "F", "Other"])
        
        occupancy_data.append({
            "id": i + 1,
            "room_id": room_id,
            "patient_id": patient_id,
            "assigned_at": assigned_at,
            "discharged_at": discharged_at,
            "attendee": attendee,
            "age_at_adm": age_at_adm,
            "gender": gender
        })
    
    return pd.DataFrame(occupancy_data)


def generate_mock_patient_records():
    """Generate mock patient records."""
    patient_data = []
    
    for i in range(200):
        patient_id = 1000 + i
        gender = random.choice(["M", "F", "Other"])
        age = random.randint(18, 85)
        date_of_birth = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
        
        admission_reasons = [
            "Chest pain", "Shortness of breath", "Abdominal pain", "Trauma",
            "Infection", "Surgery", "Follow-up", "Emergency", "Routine check"
        ]
        
        patient_data.append({
            "id": patient_id,
            "gender": gender,
            "date_of_birth": date_of_birth.date(),
            "age_at_adm": age,
            "admission_reason": random.choice(admission_reasons),
            "previous_visits": random.randint(0, 5)
        })
    
    return pd.DataFrame(patient_data)


def generate_mock_users():
    """Generate mock users/staff data."""
    staff_data = [
        {"id": 1, "full_name": "Dr. Sarah Johnson", "staff_type": "doctors", "department": "Emergency", "shift_pattern": "rotating", "status": "active"},
        {"id": 2, "full_name": "Dr. Michael Brown", "staff_type": "doctors", "department": "ICU", "shift_pattern": "day", "status": "active"},
        {"id": 3, "full_name": "Dr. Emily Davis", "staff_type": "doctors", "department": "Surgery", "shift_pattern": "day", "status": "active"},
        {"id": 4, "full_name": "Nurse Jennifer Wilson", "staff_type": "nurses", "department": "ICU", "shift_pattern": "rotating", "status": "active"},
        {"id": 5, "full_name": "Nurse Robert Miller", "staff_type": "nurses", "department": "Emergency", "shift_pattern": "night", "status": "active"},
        {"id": 6, "full_name": "Nurse Lisa Garcia", "staff_type": "nurses", "department": "General", "shift_pattern": "day", "status": "active"},
        {"id": 7, "full_name": "Nurse Maria Rodriguez", "staff_type": "nurses", "department": "Pediatric", "shift_pattern": "day", "status": "active"},
        {"id": 8, "full_name": "Tech John Anderson", "staff_type": "support", "department": "General", "shift_pattern": "day", "status": "active"},
        {"id": 9, "full_name": "Tech Amanda Taylor", "staff_type": "support", "department": "ICU", "shift_pattern": "rotating", "status": "active"},
        {"id": 10, "full_name": "Dr. David Lee", "staff_type": "doctors", "department": "Pediatric", "shift_pattern": "day", "status": "active"},
    ]
    
    # Add more nurses to have realistic ratios
    for i in range(15):
        staff_data.append({
            "id": 11 + i,
            "full_name": f"Nurse Staff-{i+1}",
            "staff_type": "nurses",
            "department": random.choice(["ICU", "Emergency", "General", "Surgical", "Pediatric"]),
            "shift_pattern": random.choice(["day", "night", "rotating"]),
            "status": "active"
        })
    
    return pd.DataFrame(staff_data)


def generate_mock_tools():
    """Generate mock tools/equipment data."""
    tools_data = [
        {"id": 1, "tool_name": "Ventilator", "quantity_total": 10, "quantity_available": 3, "quantity_in_use": 7, "maintenance_status": "good", "status": "active"},
        {"id": 2, "tool_name": "ECG Machine", "quantity_total": 15, "quantity_available": 8, "quantity_in_use": 7, "maintenance_status": "good", "status": "active"},
        {"id": 3, "tool_name": "Defibrillator", "quantity_total": 8, "quantity_available": 2, "quantity_in_use": 6, "maintenance_status": "good", "status": "active"},
        {"id": 4, "tool_name": "X-Ray Machine", "quantity_total": 4, "quantity_available": 1, "quantity_in_use": 3, "maintenance_status": "maintenance", "status": "active"},
        {"id": 5, "tool_name": "Ultrasound", "quantity_total": 6, "quantity_available": 2, "quantity_in_use": 4, "maintenance_status": "good", "status": "active"},
        {"id": 6, "tool_name": "Patient Monitor", "quantity_total": 25, "quantity_available": 5, "quantity_in_use": 20, "maintenance_status": "good", "status": "active"},
        {"id": 7, "tool_name": "Wheelchair", "quantity_total": 20, "quantity_available": 12, "quantity_in_use": 8, "maintenance_status": "good", "status": "active"},
        {"id": 8, "tool_name": "IV Pump", "quantity_total": 30, "quantity_available": 8, "quantity_in_use": 22, "maintenance_status": "good", "status": "active"},
    ]
    return pd.DataFrame(tools_data)


def generate_mock_inventory():
    """Generate mock hospital inventory data."""
    inventory_items = [
        {"item_name": "Surgical Gloves", "category": "Medical Supplies", "quantity_available": 500, "unit_cost": 0.25},
        {"item_name": "Face Masks", "category": "Medical Supplies", "quantity_available": 1200, "unit_cost": 0.15},
        {"item_name": "Syringes", "category": "Medical Supplies", "quantity_available": 800, "unit_cost": 0.30},
        {"item_name": "Gauze Pads", "category": "Medical Supplies", "quantity_available": 300, "unit_cost": 0.50},
        {"item_name": "Acetaminophen", "category": "Pharmaceuticals", "quantity_available": 150, "unit_cost": 2.50},
        {"item_name": "Ibuprofen", "category": "Pharmaceuticals", "quantity_available": 200, "unit_cost": 1.80},
        {"item_name": "Amoxicillin", "category": "Pharmaceuticals", "quantity_available": 75, "unit_cost": 8.50},
        {"item_name": "Saline Solution", "category": "Pharmaceuticals", "quantity_available": 300, "unit_cost": 3.20},
        {"item_name": "Surgical Sutures", "category": "Surgical Supplies", "quantity_available": 80, "unit_cost": 15.00},
        {"item_name": "Scalpels", "category": "Surgical Supplies", "quantity_available": 50, "unit_cost": 12.00},
        {"item_name": "Bandages", "category": "Medical Supplies", "quantity_available": 400, "unit_cost": 1.20},
        {"item_name": "Alcohol Wipes", "category": "Disposables", "quantity_available": 2000, "unit_cost": 0.05},
        {"item_name": "Paper Towels", "category": "Disposables", "quantity_available": 100, "unit_cost": 2.00},
        {"item_name": "Bed Sheets", "category": "Linens", "quantity_available": 60, "unit_cost": 15.00},
        {"item_name": "Pillowcases", "category": "Linens", "quantity_available": 80, "unit_cost": 8.00},
    ]
    
    inventory_data = []
    for i, item in enumerate(inventory_items):
        inventory_data.append({
            "id": i + 1,
            "item_name": item["item_name"],
            "category": item["category"],
            "quantity_available": item["quantity_available"],
            "expiry_date": datetime.now() + timedelta(days=random.randint(30, 365)),
            "supplier": f"Supplier-{random.randint(1, 5)}",
            "unit_cost": item["unit_cost"],
            "status": "active"
        })
    
    return pd.DataFrame(inventory_data)


class MockDB:
    """Mock database that provides the same interface as the real database."""
    
    def __init__(self):
        self._data = {
            'rooms': generate_mock_rooms(),
            'occupancy': generate_mock_occupancy(),
            'patient_records': generate_mock_patient_records(),
            'users': generate_mock_users(),
            'tools': generate_mock_tools(),
            'hospital_inventory': generate_mock_inventory(),
        }
    
    def get_rooms(self):
        return self._data['rooms']
    
    def get_occupancy(self, days_back=90):
        df = self._data['occupancy'].copy()
        cutoff = datetime.now() - timedelta(days=days_back)
        return df[df['assigned_at'] >= cutoff]
    
    def get_patient_records(self):
        return self._data['patient_records']
    
    def get_users(self):
        return self._data['users']
    
    def get_tools(self):
        return self._data['tools']
    
    def get_inventory(self):
        return self._data['hospital_inventory']
    
    def execute_query(self, query, params=None):
        """Mock query execution for basic tests."""
        if "SELECT 1 as test" in query:
            return pd.DataFrame({"test": [1]})
        else:
            raise Exception("Mock DB: Query not supported in mock mode")


# Global mock database instance
mock_db = MockDB() 