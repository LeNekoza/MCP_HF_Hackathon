"""
Bed occupancy analytics module.
Provides real-time bed occupancy snapshots by ward.
"""
import pandas as pd
from datetime import datetime
from ..db_utils import db


def get_bed_snapshot(date: str = None) -> dict:
    """
    Get current bed occupancy snapshot by ward.
    
    Args:
        date: Optional date string (YYYY-MM-DD). If None, uses current date.
        
    Returns:
        Dictionary with ward-level occupancy data for chart rendering.
    """
    # Get rooms and current occupancy data
    rooms = db.get_rooms()
    occupancy = db.get_occupancy(days_back=30)
    
    # Filter for active occupancies (not discharged or discharged after now)
    now = pd.Timestamp.utcnow()
    active_now = occupancy[
        (occupancy["discharged_at"].isna()) | 
        (occupancy["discharged_at"] > now)
    ].copy()
    
    # Map room types
    room_type_map = rooms.set_index("id")["room_type"].to_dict()
    active_now["room_type"] = active_now["room_id"].map(room_type_map)
    
    # Calculate occupancy by ward
    occ_by_ward = (
        active_now.groupby("room_type").size()
        .rename("current_occupied_beds")
        .to_frame()
    )
    
    # Get total bed capacity by ward
    total_beds = rooms.groupby("room_type")["bed_capacity"].sum()
    
    # Combine data
    result = occ_by_ward.join(total_beds, how="outer").fillna(0)
    result["available_beds"] = result["bed_capacity"] - result["current_occupied_beds"]
    result["utilisation_pct"] = (
        result["current_occupied_beds"] / result["bed_capacity"] * 100
    ).round(1)
    
    # Format for chart rendering
    data = []
    for ward, row in result.iterrows():
        data.append({
            "ward": ward,
            "occupied": int(row["current_occupied_beds"]),
            "available": int(row["available_beds"]),
            "total": int(row["bed_capacity"]),
            "utilisation": float(row["utilisation_pct"])
        })
    
    return {
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "total_beds": int(result["bed_capacity"].sum()),
        "total_occupied": int(result["current_occupied_beds"].sum()),
        "overall_utilisation": round(
            result["current_occupied_beds"].sum() / result["bed_capacity"].sum() * 100, 1
        )
    } 