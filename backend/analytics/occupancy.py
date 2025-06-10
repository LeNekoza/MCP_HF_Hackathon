"""
Bed occupancy analytics and snapshots
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from ..database import get_rooms, get_occupancy
from ..storage import save_analysis_result, save_model_data


def get_bed_snapshot(date: datetime = None, save_results: bool = True) -> Dict[str, Any]:
    """
    Get real-time bed occupancy by ward
    
    Args:
        date: Optional date for snapshot (defaults to current time)
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with ward-level occupancy data
    """
    if date is None:
        date = pd.Timestamp.utcnow().tz_localize(None)  # Remove timezone for compatibility
    
    # Load data
    rooms = get_rooms()
    occupancy = get_occupancy()
    
    # Clean column names
    for df in (rooms, occupancy):
        df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], 
                inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'assigned_at' in occupancy.columns:
        occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
    if 'discharged_at' in occupancy.columns:
        occupancy['discharged_at'] = pd.to_datetime(occupancy['discharged_at'])
    
    # Create room type mapping
    room_type_map = rooms.set_index("id")["room_type"]
    
    # Find currently active occupancies
    # Convert date to pandas datetime for comparison
    if not isinstance(date, pd.Timestamp):
        date = pd.to_datetime(date)
    
    active_now = occupancy[
        (occupancy["discharged_at"].isna()) | 
        (occupancy["discharged_at"] > date)
    ].copy()
    
    active_now["room_type"] = active_now["room_id"].map(room_type_map)
    
    # Calculate occupancy by ward
    occ_summary = (
        active_now.groupby("room_type").size()
        .rename("current_occupied_beds").to_frame()
        .join(rooms.groupby("room_type")["bed_capacity"].sum().rename("total_beds"))
        .fillna(0)
    )
    
    occ_summary["utilisation_pct"] = (
        occ_summary.current_occupied_beds / occ_summary.total_beds * 100
    ).round(1)
    
    # Convert to JSON-friendly format
    result = {
        "timestamp": date.isoformat(),
        "wards": []
    }
    
    for ward, row in occ_summary.iterrows():
        result["wards"].append({
            "ward_type": ward,
            "occupied_beds": int(row.current_occupied_beds),
            "total_beds": int(row.total_beds),
            "utilisation_pct": float(row.utilisation_pct)
        })
    
    # Calculate totals
    total_occupied = int(occ_summary.current_occupied_beds.sum())
    total_capacity = int(occ_summary.total_beds.sum())
    
    # Handle division by zero
    if total_capacity > 0:
        overall_util = float((total_occupied / total_capacity * 100).round(1))
    else:
        overall_util = 0.0
    
    result["summary"] = {
        "total_occupied": total_occupied,
        "total_capacity": total_capacity,
        "overall_utilisation_pct": overall_util
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data (JSON)
        save_analysis_result("bed_snapshot", result)
        
        # Force CSV generation
        save_analysis_result("bed_snapshot", result, format="csv")
        
        # Save model/configuration data
        model_data = {
            "analysis_type": "bed_snapshot",
            "snapshot_date": date.isoformat(),
            "total_wards": len(result["wards"]),
            "ward_types": [ward["ward_type"] for ward in result["wards"]],
            "calculation_method": "real_time_occupancy",
            "data_sources": ["rooms", "occupancy"],
            "utilization_formula": "occupied_beds / total_beds * 100"
        }
        save_model_data("bed_snapshot", model_data)
    
    return result 