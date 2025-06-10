"""
Average Length of Stay (ALOS) analytics by ward
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from ..database import get_occupancy, get_rooms
from ..storage import save_analysis_result, save_model_data


def average_los_by_ward(save_results: bool = True) -> Dict[str, Any]:
    """
    Calculate average length of stay by ward type
    
    Args:
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with average LOS data by ward
    """
    # Load data
    occupancy = get_occupancy()
    rooms = get_rooms()
    
    # Clean data
    for df in (occupancy, rooms):
        df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], 
               inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'assigned_at' in occupancy.columns:
        occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
    if 'discharged_at' in occupancy.columns:
        occupancy['discharged_at'] = pd.to_datetime(occupancy['discharged_at'])
    
    # Calculate LOS for completed stays only
    los_df = occupancy.dropna(subset=["discharged_at"]).copy()
    los_df["los_days"] = (
        los_df.discharged_at - los_df.assigned_at
    ).dt.total_seconds() / 86400
    
    # Add room type mapping
    room_type_map = rooms.set_index("id")["room_type"]
    los_df["room_type"] = los_df["room_id"].map(room_type_map)
    
    # Filter realistic LOS values (0-365 days)
    los_df = los_df[los_df.los_days.between(0, 365)]
    
    # Calculate average LOS by ward
    alos_stats = los_df.groupby("room_type")["los_days"].agg([
        'mean', 'median', 'std', 'count', 'min', 'max'
    ]).round(2)
    
    # Convert to JSON format
    ward_data = []
    for ward, stats in alos_stats.iterrows():
        ward_data.append({
            "ward_type": ward,
            "avg_los_days": float(stats['mean']),
            "median_los_days": float(stats['median']),
            "std_los_days": float(stats['std']) if pd.notnull(stats['std']) else 0.0,
            "min_los_days": float(stats['min']),
            "max_los_days": float(stats['max']),
            "total_discharges": int(stats['count'])
        })
    
    # Overall statistics
    overall_stats = {
        "overall_avg_los": float(los_df['los_days'].mean()),
        "overall_median_los": float(los_df['los_days'].median()),
        "overall_std_los": float(los_df['los_days'].std()),
        "total_completed_stays": len(los_df),
        "analysis_period_days": (
            los_df.discharged_at.max() - los_df.assigned_at.min()
        ).days if len(los_df) > 0 else 0
    }
    
    result = {
        "ward_statistics": ward_data,
        "overall_statistics": overall_stats,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data
        save_analysis_result("average_los", result)
        
        # Also save as CSV for tabular data
        if ward_data:
            ward_df = pd.DataFrame(ward_data)
            save_analysis_result("average_los", {"ward_data": ward_df.to_dict('records')}, format="csv")
        
        # Save model/analysis data
        model_data = {
            "analysis_type": "average_los",
            "calculation_method": "completed_stays_only",
            "los_range_filter": "0-365 days",
            "statistics_computed": ["mean", "median", "std", "count", "min", "max"],
            "ward_breakdown": {
                "total_wards": len(ward_data),
                "wards_analyzed": [w["ward_type"] for w in ward_data]
            },
            "overall_metrics": overall_stats,
            "data_quality": {
                "total_records_processed": len(los_df),
                "completed_stays_only": True,
                "outliers_filtered": True
            }
        }
        save_model_data("average_los", model_data)
    
    return result 