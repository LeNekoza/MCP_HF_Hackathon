"""
Admission split analytics (elective vs emergency)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from ..database import get_occupancy
from ..storage import save_analysis_result, save_model_data


def admission_split(days_back: int = 14, save_results: bool = True) -> Dict[str, Any]:
    """
    Analyze elective vs emergency admission patterns
    
    Args:
        days_back: Number of days to analyze from current date
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with admission split data
    """
    # Load data
    occupancy = get_occupancy()
    
    # Clean data
    occupancy.drop(columns=[c for c in occupancy.columns if c.startswith("Unnamed")], 
                   inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'assigned_at' in occupancy.columns:
        occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
    
    # Filter to recent data
    cutoff_date = pd.Timestamp.utcnow().tz_localize(None) - timedelta(days=days_back)
    recent_occupancy = occupancy[occupancy['assigned_at'] >= cutoff_date].copy()
    
    # Classify admissions based on time of day
    # Elective: 8 AM - 5 PM (business hours)
    # Emergency: all other times
    recent_occupancy['admission_type'] = np.where(
        recent_occupancy['assigned_at'].dt.hour.between(8, 17),
        'Elective',
        'Emergency'
    )
    
    # Overall split
    overall_split = recent_occupancy['admission_type'].value_counts()
    total_admissions = len(recent_occupancy)
    
    overall_data = []
    for admission_type, count in overall_split.items():
        overall_data.append({
            'admission_type': admission_type,
            'count': int(count),
            'percentage': float(round(count / total_admissions * 100, 1))
        })
    
    # Daily breakdown
    daily_breakdown = (
        recent_occupancy.groupby([
            recent_occupancy['assigned_at'].dt.date, 
            'admission_type'
        ]).size()
        .unstack(fill_value=0)
        .reset_index()
    )
    
    daily_data = []
    for _, row in daily_breakdown.iterrows():
        date_str = row['assigned_at'].strftime('%Y-%m-%d')
        elective_count = int(row.get('Elective', 0))
        emergency_count = int(row.get('Emergency', 0))
        total_day = elective_count + emergency_count
        
        daily_data.append({
            'date': date_str,
            'elective_count': elective_count,
            'emergency_count': emergency_count,
            'total_admissions': total_day,
            'elective_pct': float(round(
                elective_count / total_day * 100 if total_day > 0 else 0, 1
            )),
            'emergency_pct': float(round(
                emergency_count / total_day * 100 if total_day > 0 else 0, 1
            ))
        })
    
    # Hourly pattern analysis
    hourly_pattern = (
        recent_occupancy.groupby([
            recent_occupancy['assigned_at'].dt.hour,
            'admission_type'
        ]).size()
        .unstack(fill_value=0)
        .reset_index()
    )
    
    hourly_data = []
    for _, row in hourly_pattern.iterrows():
        hour = int(row['assigned_at'])
        elective_count = int(row.get('Elective', 0))
        emergency_count = int(row.get('Emergency', 0))
        
        hourly_data.append({
            'hour': hour,
            'hour_label': f"{hour:02d}:00",
            'elective_count': elective_count,
            'emergency_count': emergency_count
        })
    
    # Summary statistics
    avg_daily_elective = overall_split.get('Elective', 0) / days_back
    avg_daily_emergency = overall_split.get('Emergency', 0) / days_back
    
    result = {
        'analysis_period': {
            'days_analyzed': days_back,
            'start_date': cutoff_date.strftime('%Y-%m-%d'),
            'end_date': pd.Timestamp.utcnow().tz_localize(None).strftime('%Y-%m-%d'),
            'total_admissions': total_admissions
        },
        'overall_split': overall_data,
        'daily_breakdown': daily_data,
        'hourly_pattern': hourly_data,
        'summary_stats': {
            'avg_daily_elective': float(round(avg_daily_elective, 1)),
            'avg_daily_emergency': float(round(avg_daily_emergency, 1)),
            'peak_elective_hour': int(
                hourly_pattern.loc[
                    hourly_pattern.get('Elective', pd.Series([0])).idxmax(), 
                    'assigned_at'
                ] if len(hourly_pattern) > 0 and 'Elective' in hourly_pattern.columns else 9
            ),
            'peak_emergency_hour': int(
                hourly_pattern.loc[
                    hourly_pattern.get('Emergency', pd.Series([0])).idxmax(), 
                    'assigned_at'
                ] if len(hourly_pattern) > 0 and 'Emergency' in hourly_pattern.columns else 0
            )
        }
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data (JSON)
        save_analysis_result("admission_split", result)
        
        # Force CSV generation
        save_analysis_result("admission_split", result, format="csv")
        
        # Save model/classification data
        model_data = {
            "analysis_type": "admission_split",
            "classification_rules": {
                "elective_hours": {"start": 8, "end": 17, "description": "Business hours 8 AM - 5 PM"},
                "emergency_hours": {"description": "All hours outside business hours"},
                "time_based_classification": True
            },
            "analysis_parameters": {
                "days_back": days_back,
                "total_admissions_analyzed": total_admissions
            },
            "pattern_insights": {
                "avg_daily_elective": float(round(avg_daily_elective, 1)),
                "avg_daily_emergency": float(round(avg_daily_emergency, 1)),
                "elective_percentage": float(round(overall_split.get('Elective', 0) / total_admissions * 100, 1)) if total_admissions > 0 else 0,
                "emergency_percentage": float(round(overall_split.get('Emergency', 0) / total_admissions * 100, 1)) if total_admissions > 0 else 0
            },
            "data_quality": {
                "records_processed": len(recent_occupancy),
                "date_range_covered": days_back,
                "missing_timestamps": int(recent_occupancy['assigned_at'].isna().sum())
            }
        }
        save_model_data("admission_split", model_data)
    
    return result 