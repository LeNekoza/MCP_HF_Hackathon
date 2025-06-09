"""
Staffing analytics module.
Forecasts staffing requirements based on occupancy and workload patterns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..db_utils import db


def forecast_staff(days: int = 3) -> dict:
    """
    Forecast staffing requirements for the next N days.
    
    Args:
        days: Number of days to forecast (default: 3)
        
    Returns:
        Dictionary with staffing forecast data.
    """
    # Get current data
    occupancy = db.get_occupancy(days_back=30)
    users = db.get_users()
    rooms = db.get_rooms()
    
    if occupancy.empty or users.empty or rooms.empty:
        return {
            "data": [],
            "error": "Insufficient data for staffing forecast"
        }
    
    # Calculate current bed occupancy by ward
    now = pd.Timestamp.utcnow()
    active_occupancy = occupancy[
        (occupancy["discharged_at"].isna()) | 
        (occupancy["discharged_at"] > now)
    ]
    
    # Map room types
    room_type_map = rooms.set_index("id")["room_type"].to_dict()
    active_occupancy["room_type"] = active_occupancy["room_id"].map(room_type_map)
    
    # Current occupancy by ward
    current_ward_occupancy = active_occupancy.groupby("room_type").size()
    
    # Define staffing ratios by ward type and shift
    staffing_ratios = {
        "ICU": {
            "nurses": {"day": 1.5, "night": 1.2},  # nurses per bed
            "doctors": {"day": 0.3, "night": 0.1},
            "support": {"day": 0.2, "night": 0.1}
        },
        "Emergency": {
            "nurses": {"day": 1.0, "night": 0.8},
            "doctors": {"day": 0.4, "night": 0.2},
            "support": {"day": 0.3, "night": 0.2}
        },
        "General Ward": {
            "nurses": {"day": 0.4, "night": 0.3},
            "doctors": {"day": 0.1, "night": 0.05},
            "support": {"day": 0.15, "night": 0.1}
        },
        "Surgical": {
            "nurses": {"day": 0.6, "night": 0.4},
            "doctors": {"day": 0.2, "night": 0.1},
            "support": {"day": 0.2, "night": 0.15}
        },
        "Pediatric": {
            "nurses": {"day": 0.8, "night": 0.6},
            "doctors": {"day": 0.15, "night": 0.08},
            "support": {"day": 0.2, "night": 0.15}
        }
    }
    
    # Get current staff by type
    staff_by_type = users.groupby("staff_type").size()
    
    # Calculate historical occupancy trends
    historical_occupancy = []
    for i in range(7, 0, -1):  # Last 7 days
        date = (datetime.now() - timedelta(days=i)).date()
        day_occupancy = occupancy[
            (occupancy["assigned_at"].dt.date <= date) &
            ((occupancy["discharged_at"].isna()) | 
             (occupancy["discharged_at"].dt.date > date))
        ]
        day_occupancy["room_type"] = day_occupancy["room_id"].map(room_type_map)
        daily_ward_occupancy = day_occupancy.groupby("room_type").size()
        historical_occupancy.append({
            "date": date.strftime("%Y-%m-%d"),
            "occupancy": daily_ward_occupancy.to_dict()
        })
    
    # Simple trend calculation (average change per day)
    if len(historical_occupancy) >= 2:
        trend_data = {}
        for ward in current_ward_occupancy.index:
            recent_values = [
                day["occupancy"].get(ward, 0) 
                for day in historical_occupancy[-3:]
            ]
            if len(recent_values) >= 2:
                trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                trend_data[ward] = trend
            else:
                trend_data[ward] = 0
    else:
        trend_data = {ward: 0 for ward in current_ward_occupancy.index}
    
    # Forecast occupancy and staffing
    forecast_data = []
    for day in range(1, days + 1):
        forecast_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        
        # Predict occupancy with trend
        predicted_occupancy = {}
        for ward, current_occ in current_ward_occupancy.items():
            trend = trend_data.get(ward, 0)
            predicted = max(0, current_occ + (trend * day))
            # Add some random variation
            predicted *= np.random.uniform(0.9, 1.1)
            predicted_occupancy[ward] = round(predicted)
        
        # Calculate required staff by ward and shift
        ward_requirements = []
        for ward, predicted_beds in predicted_occupancy.items():
            ward_ratios = staffing_ratios.get(ward, staffing_ratios["General Ward"])
            
            day_requirements = {}
            night_requirements = {}
            
            for staff_type, ratios in ward_ratios.items():
                day_requirements[staff_type] = max(1, round(predicted_beds * ratios["day"]))
                night_requirements[staff_type] = max(1, round(predicted_beds * ratios["night"]))
            
            ward_requirements.append({
                "ward": ward,
                "predicted_occupancy": predicted_beds,
                "day_shift": day_requirements,
                "night_shift": night_requirements
            })
        
        # Calculate total requirements
        total_day = {"nurses": 0, "doctors": 0, "support": 0}
        total_night = {"nurses": 0, "doctors": 0, "support": 0}
        
        for ward_req in ward_requirements:
            for staff_type in total_day.keys():
                total_day[staff_type] += ward_req["day_shift"].get(staff_type, 0)
                total_night[staff_type] += ward_req["night_shift"].get(staff_type, 0)
        
        # Compare with available staff
        available_staff = staff_by_type.to_dict()
        
        day_shortfall = {}
        night_shortfall = {}
        
        for staff_type, required in total_day.items():
            available = available_staff.get(staff_type, 0)
            day_shortfall[staff_type] = max(0, required - available // 2)  # Assume staff split between shifts
        
        for staff_type, required in total_night.items():
            available = available_staff.get(staff_type, 0)
            night_shortfall[staff_type] = max(0, required - available // 2)
        
        forecast_data.append({
            "date": forecast_date,
            "ward_requirements": ward_requirements,
            "total_requirements": {
                "day_shift": total_day,
                "night_shift": total_night
            },
            "shortfalls": {
                "day_shift": day_shortfall,
                "night_shift": night_shortfall
            },
            "total_predicted_occupancy": sum(predicted_occupancy.values())
        })
    
    # Calculate summary metrics
    total_shortfalls = {"day": {}, "night": {}}
    for day_forecast in forecast_data:
        for staff_type in ["nurses", "doctors", "support"]:
            if staff_type not in total_shortfalls["day"]:
                total_shortfalls["day"][staff_type] = 0
                total_shortfalls["night"][staff_type] = 0
            
            total_shortfalls["day"][staff_type] += day_forecast["shortfalls"]["day_shift"].get(staff_type, 0)
            total_shortfalls["night"][staff_type] += day_forecast["shortfalls"]["night_shift"].get(staff_type, 0)
    
    # Check for critical shortfalls
    critical_shortfalls = []
    for shift, shortfalls in total_shortfalls.items():
        for staff_type, total_shortage in shortfalls.items():
            if total_shortage > 0:
                critical_shortfalls.append({
                    "shift": shift,
                    "staff_type": staff_type,
                    "total_shortage": total_shortage,
                    "severity": "critical" if total_shortage > 5 else "moderate"
                })
    
    return {
        "forecast": forecast_data,
        "summary": {
            "current_total_occupancy": int(current_ward_occupancy.sum()),
            "current_staff_count": staff_by_type.to_dict(),
            "critical_shortfalls": critical_shortfalls,
            "forecast_period": f"{days} days"
        },
        "historical_trend": historical_occupancy[-7:],  # Last 7 days
        "timestamp": datetime.now().isoformat()
    } 