# NeonDB PostgreSQL Integration

## Overview

This project now includes full integration with NeonDB PostgreSQL for hospital data management. The integration provides data retrieval capabilities for your MCP HF Hackathon application.

## 🚀 Quick Start

### 1. Database Connection Test
```bash
# Activate virtual environment
source env/bin/activate

# Test database connection
python test_database.py
```

### 2. Run Example Usage
```bash
# See comprehensive examples
python example_database_usage.py
```

### 3. Test Gradio Interface
```bash
# Launch database interface
python test_gradio_database.py
```

## 📊 Database Overview

Your NeonDB instance contains **8,110 total records** across 7 tables:

| Table | Records | Description |
|-------|---------|-------------|
| `users` | 3,210 | User accounts (patients, staff, admins) |
| `patient_records` | 3,000 | Patient medical records |
| `rooms` | 150 | Hospital room details |
| `occupancy` | 1,100 | Room occupancy records |
| `tools` | 500 | Medical tools and equipment |
| `hospital_inventory` | 100 | Hospital inventory items |
| `storage_rooms` | 50 | Hospital storage room information |

## 🔧 Configuration

### Database Credentials
Your database is configured with the following settings:
- **Host**: `ep-red-feather-a1hmmdyu-pooler.ap-southeast-1.aws.neon.tech`
- **Database**: `maindb`
- **User**: `maindb_owner`
- **Port**: 5432
- **SSL**: Required

### Files Created
- `neon_config.json` - Database configuration (already set up)
- `src/utils/database.py` - Database connection and query utilities
- `src/components/database_interface.py` - Gradio interface components

## 📚 Usage Examples

### Basic Data Retrieval
```python
from src.utils.database import get_data_retriever

# Initialize data retriever
retriever = get_data_retriever()

# Get database statistics
stats = retriever.get_database_stats()
print(f"Total users: {stats['users']}")

# Search for patients
patients = retriever.search_patients_by_name("John")
print(f"Found {len(patients)} patients named John")

# Get available rooms
rooms = retriever.get_rooms(available_only=True)
print(f"Available rooms: {len(rooms)}")

# Get medical equipment
equipment = retriever.get_medical_equipment(available_only=True)
print(f"Available equipment: {len(equipment)}")
```

### API Integration Example
```python
def get_patient_api_response(patient_name: str) -> dict:
    retriever = get_data_retriever()
    patients_df = retriever.search_patients_by_name(patient_name)
    
    return {
        "status": "success",
        "count": len(patients_df),
        "data": patients_df.to_dict('records')
    }
```

### Gradio Integration
```python
from src.components.database_interface import create_database_tab

# Add to your Gradio interface
with gr.Tabs():
    database_tab = create_database_tab()
```

## 🔍 Available Functions

### Database Connection
- `test_database_connection()` - Test database connectivity
- `get_data_retriever()` - Get configured data retriever instance

### Data Retrieval Methods
- `get_all_users(limit=None)` - Retrieve all users
- `get_patients(limit=None)` - Get patient records with user info
- `get_staff(staff_type=None, limit=None)` - Get staff members
- `get_rooms(room_type=None, available_only=False, limit=None)` - Get room information
- `get_occupancy(active_only=True)` - Get occupancy records
- `get_medical_equipment(location_id=None, available_only=False, limit=None)` - Get equipment
- `get_hospital_inventory(location_id=None, item_type=None)` - Get inventory
- `get_storage_rooms(floor_number=None)` - Get storage rooms
- `search_patients_by_name(name_pattern)` - Search patients by name
- `get_database_stats()` - Get record counts for all tables

### AI Chat Integration
- `get_patient_summary_for_ai(patient_name)` - Get patient info for AI responses
- `get_room_availability_summary()` - Get room availability for AI responses

## 🎨 Gradio Interface Features

The database interface provides:

### 📊 Database Overview
- Real-time connection status
- Database statistics and record counts
- Last updated timestamp

### 🔍 Patient Search
- Search patients by name (partial matching)
- Display patient details (ID, name, DOB, blood type, phone)
- Limit results to prevent overwhelming the interface

### 🏠 Room Availability
- Filter by room type
- Show only available rooms option
- Display room details with availability status

### 🩺 Medical Equipment
- Filter available equipment only
- Show equipment details and quantities
- Location information

### 👨‍⚕️ Medical Staff
- Filter by staff type (doctor, nurse, admin, etc.)
- Display staff information and roles

## 🛠️ Installation & Dependencies

The following packages were added to `requirements.txt`:
```
psycopg2-binary>=2.9.0
SQLAlchemy>=2.0.0
```

Already installed in your virtual environment!

## 🔒 Security Notes

- Database credentials are stored in `neon_config.json` (not committed to git)
- For production, consider using environment variables
- See `SECURITY.md` for best practices

## 🚀 Integration with Your Application

### 1. Add Database Tab to Main Interface
In your main `interface.py`, add:
```python
from .database_interface import create_database_tab

# In your main interface
with gr.Tabs():
    # Your existing tabs
    database_tab = create_database_tab()
```

### 2. Enhance AI Chat with Database Queries
```python
from .database_interface import get_patient_summary_for_ai, get_room_availability_summary

def handle_ai_response(user_message: str) -> str:
    # Check if user is asking about patients
    if "patient" in user_message.lower():
        # Extract patient name and get summary
        return get_patient_summary_for_ai(patient_name)
    
    # Check if user is asking about rooms
    if "room" in user_message.lower() and "available" in user_message.lower():
        return get_room_availability_summary()
    
    # Your existing AI logic
    return your_ai_response(user_message)
```

### 3. API Endpoints
```python
@app.route('/api/patients/<name>')
def api_get_patients(name):
    retriever = get_data_retriever()
    patients = retriever.search_patients_by_name(name)
    return patients.to_dict('records')
```

## 📈 Performance Notes

- All queries include optional `limit` parameters to prevent large data loads
- Database connections use context managers for proper cleanup
- Pandas warnings about psycopg2 connections are harmless
- Consider adding caching for frequently accessed data

## 🔧 Troubleshooting

### Connection Issues
1. Check `neon_config.json` exists and has correct credentials
2. Verify network connectivity to NeonDB
3. Run `python test_database.py` to diagnose issues

### Data Display Issues
1. Check data types in DataFrames
2. Verify column names match expected headers
3. Handle None/null values appropriately

### Performance Issues
1. Use `limit` parameters in queries
2. Consider pagination for large result sets
3. Add loading indicators in Gradio interface

## 🎯 Next Steps

1. **Integrate with Main App**: Add database tab to your main interface
2. **Enhance AI Chat**: Use database functions in AI responses
3. **Add Data Visualization**: Create charts and graphs from database data
4. **Implement Caching**: Add Redis or in-memory caching for performance
5. **Add Real-time Updates**: Implement WebSocket for live data updates

## 📞 Support

If you encounter any issues:
1. Check the logs in `logs/` directory
2. Run the test scripts to identify problems
3. Verify database credentials and connectivity
4. Check the pandas/SQLAlchemy versions for compatibility

---

**🎉 Your NeonDB PostgreSQL integration is complete and ready to use!** 