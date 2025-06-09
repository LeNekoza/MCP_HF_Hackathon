"""
Admission type analytics module.
Analyzes elective vs emergency admission patterns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..db_utils import db


def admission_split(days_back: int = 14) -> dict:
    """
    Analyze elective vs emergency admission patterns.
    
    Args:
        days_back: Number of days to look back for analysis (default: 14)
        
    Returns:
        Dictionary with admission type breakdown data.
    """
    # Get occupancy data
    occupancy = db.get_occupancy(days_back=days_back)
    
    if occupancy.empty:
        return {
            "data": [],
            "summary": {"elective": 0, "emergency": 0},
            "error": "No occupancy data found"
        }
    
    # Classify admissions based on time of day
    # Elective: 8 AM - 5 PM (business hours)
    # Emergency: All other times
    occupancy = occupancy.dropna(subset=["assigned_at"])
    occupancy["admission_hour"] = occupancy["assigned_at"].dt.hour
    occupancy["admission_type"] = np.where(
        occupancy["admission_hour"].between(8, 17),
        "Elective",
        "Emergency"
    )
    
    # Overall split
    overall_split = occupancy["admission_type"].value_counts()
    total_admissions = overall_split.sum()
    
    # Daily breakdown
    daily_split = (
        occupancy.groupby([
            occupancy["assigned_at"].dt.date, 
            "admission_type"
        ])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    daily_split["date"] = daily_split["assigned_at"].astype(str)
    
    # Format daily data for charting
    daily_data = []
    for _, row in daily_split.iterrows():
        daily_data.append({
            "date": row["date"],
            "elective": int(row.get("Elective", 0)),
            "emergency": int(row.get("Emergency", 0)),
            "total": int(row.get("Elective", 0) + row.get("Emergency", 0))
        })
    
    # Weekly patterns
    occupancy["day_of_week"] = occupancy["assigned_at"].dt.day_name()
    weekly_pattern = (
        occupancy.groupby(["day_of_week", "admission_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    
    weekly_data = []
    for _, row in weekly_pattern.iterrows():
        weekly_data.append({
            "day": row["day_of_week"],
            "elective": int(row.get("Elective", 0)),
            "emergency": int(row.get("Emergency", 0))
        })
    
    # Hourly distribution
    hourly_pattern = (
        occupancy.groupby(["admission_hour", "admission_type"])
        .size()
        .unstack(fill_value=0)
        .fillna(0)
        .reset_index()
    )
    
    hourly_data = []
    for _, row in hourly_pattern.iterrows():
        hourly_data.append({
            "hour": int(row["admission_hour"]),
            "elective": int(row.get("Elective", 0)),
            "emergency": int(row.get("Emergency", 0))
        })
    
    # Summary statistics
    summary = {
        "elective_count": int(overall_split.get("Elective", 0)),
        "emergency_count": int(overall_split.get("Emergency", 0)),
        "elective_percentage": round(
            overall_split.get("Elective", 0) / total_admissions * 100, 1
        ) if total_admissions > 0 else 0,
        "emergency_percentage": round(
            overall_split.get("Emergency", 0) / total_admissions * 100, 1
        ) if total_admissions > 0 else 0,
        "total_admissions": int(total_admissions),
        "analysis_period": f"{days_back} days"
    }
    
    return {
        "daily_data": daily_data,
        "weekly_pattern": weekly_data,
        "hourly_distribution": hourly_data,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    } 