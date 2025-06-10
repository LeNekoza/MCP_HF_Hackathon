"""
Staffing requirements analytics and forecasting
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from ..database import get_occupancy, get_rooms, get_users
from ..storage import save_analysis_result, save_model_data


def forecast_staff(days: int = 3, save_results: bool = True) -> Dict[str, Any]:
    """
    Forecast staffing requirements based on bed occupancy and patient load
    
    Args:
        days: Number of days to forecast ahead
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with staffing forecast data
    """
    # Load data
    occupancy = get_occupancy()
    rooms = get_rooms()
    users = get_users()
    
    # Clean data
    for df in (occupancy, rooms, users):
        df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], 
               inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'assigned_at' in occupancy.columns:
        occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
    if 'discharged_at' in occupancy.columns:
        occupancy['discharged_at'] = pd.to_datetime(occupancy['discharged_at'])
    
    # Get current occupancy by ward
    current_date = pd.Timestamp.utcnow().tz_localize(None)
    room_type_map = rooms.set_index("id")["room_type"]
    
    # Current active patients
    active_patients = occupancy[
        (occupancy["discharged_at"].isna()) | 
        (occupancy["discharged_at"] > current_date)
    ].copy()
    
    active_patients["room_type"] = active_patients["room_id"].map(room_type_map)
    
    # Current occupancy by ward
    current_occupancy = active_patients.groupby("room_type").size().to_dict()
    
    # Calculate staffing requirements based on standard ratios
    staffing_ratios = _get_staffing_ratios()
    
    forecast_data = []
    
    for day_offset in range(days):
        forecast_date = current_date + timedelta(days=day_offset)
        
        # Estimate occupancy for forecast date (simplified - would use census forecast in practice)
        occupancy_factor = _estimate_occupancy_factor(day_offset)
        
        day_requirements = {}
        
        for ward_type in current_occupancy.keys():
            estimated_patients = int(current_occupancy[ward_type] * occupancy_factor)
            
            # Calculate required staff by type
            ratios = staffing_ratios.get(ward_type, staffing_ratios['General'])
            
            day_requirements[ward_type] = {
                'estimated_patients': estimated_patients,
                'nurses_day': max(1, int(estimated_patients / ratios['nurse_patient_ratio_day'])),
                'nurses_night': max(1, int(estimated_patients / ratios['nurse_patient_ratio_night'])),
                'doctors': max(1, int(estimated_patients / ratios['doctor_patient_ratio'])),
                'support_staff': max(1, int(estimated_patients / ratios['support_patient_ratio']))
            }
        
        forecast_data.append({
            'date': forecast_date.strftime('%Y-%m-%d'),
            'day_of_week': forecast_date.strftime('%A'),
            'ward_requirements': day_requirements,
            'total_requirements': _calculate_totals(day_requirements)
        })
    
    # Current staff analysis
    current_staff = _analyze_current_staff(users)
    
    # Generate recommendations
    recommendations = _generate_staffing_recommendations(forecast_data, current_staff)
    
    result = {
        'forecast_period_days': days,
        'current_date': current_date.strftime('%Y-%m-%d'),
        'current_occupancy': current_occupancy,
        'current_staff': current_staff,
        'daily_forecasts': forecast_data,
        'recommendations': recommendations,
        'staffing_ratios_used': staffing_ratios
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data (JSON)
        save_analysis_result("staffing", result)
        
        # Force CSV generation
        save_analysis_result("staffing", result, format="csv")
        
        # Save model/staffing data
        model_data = {
            "analysis_type": "staffing",
            "forecast_parameters": {
                "forecast_days": days,
                "occupancy_estimation_method": "factor_based",
                "weekend_adjustment_factor": 0.85,
                "variation_range": "0.7-1.3"
            },
            "staffing_ratios": staffing_ratios,
            "calculation_methodology": {
                "nurse_requirements": "Based on patient-to-nurse ratios by ward type",
                "doctor_requirements": "Based on patient-to-doctor ratios by ward type",
                "support_requirements": "Based on patient-to-support staff ratios",
                "minimum_staff": "At least 1 staff member per category per ward"
            },
            "current_staff_analysis": current_staff,
            "forecast_quality": {
                "wards_analyzed": len(current_occupancy),
                "total_current_patients": sum(current_occupancy.values()),
                "total_current_staff": current_staff.get('total_staff', 0),
                "recommendations_generated": len(recommendations)
            },
            "ward_types_supported": list(staffing_ratios.keys())
        }
        save_model_data("staffing", model_data)
    
    return result


def _get_staffing_ratios() -> Dict[str, Dict[str, float]]:
    """Define standard staffing ratios by ward type"""
    return {
        'ICU': {
            'nurse_patient_ratio_day': 1.0,    # 1:1 ratio
            'nurse_patient_ratio_night': 1.5,  # 1:1.5 ratio
            'doctor_patient_ratio': 4.0,       # 1:4 ratio
            'support_patient_ratio': 8.0       # 1:8 ratio
        },
        'Emergency': {
            'nurse_patient_ratio_day': 2.0,    # 1:2 ratio
            'nurse_patient_ratio_night': 3.0,  # 1:3 ratio
            'doctor_patient_ratio': 6.0,       # 1:6 ratio
            'support_patient_ratio': 12.0      # 1:12 ratio
        },
        'General': {
            'nurse_patient_ratio_day': 4.0,    # 1:4 ratio
            'nurse_patient_ratio_night': 6.0,  # 1:6 ratio
            'doctor_patient_ratio': 10.0,      # 1:10 ratio
            'support_patient_ratio': 15.0      # 1:15 ratio
        },
        'Pediatric': {
            'nurse_patient_ratio_day': 3.0,    # 1:3 ratio
            'nurse_patient_ratio_night': 4.0,  # 1:4 ratio
            'doctor_patient_ratio': 8.0,       # 1:8 ratio
            'support_patient_ratio': 12.0      # 1:12 ratio
        },
        'Maternity': {
            'nurse_patient_ratio_day': 3.0,    # 1:3 ratio
            'nurse_patient_ratio_night': 4.0,  # 1:4 ratio
            'doctor_patient_ratio': 8.0,       # 1:8 ratio
            'support_patient_ratio': 12.0      # 1:12 ratio
        }
    }


def _estimate_occupancy_factor(day_offset: int) -> float:
    """Estimate occupancy factor for future days"""
    # Simple model - in practice would use census forecast
    # Weekend effect (lower occupancy on weekends)
    current_date = pd.Timestamp.utcnow()
    forecast_date = current_date + timedelta(days=day_offset)
    
    base_factor = 1.0
    
    # Weekend adjustment
    if forecast_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        base_factor *= 0.85
    
    # Slight random variation
    variation = np.random.normal(1.0, 0.05)
    
    return base_factor * max(0.7, min(1.3, variation))


def _calculate_totals(ward_requirements: Dict) -> Dict[str, int]:
    """Calculate total staff requirements across all wards"""
    totals = {
        'nurses_day': 0,
        'nurses_night': 0,
        'doctors': 0,
        'support_staff': 0,
        'total_patients': 0
    }
    
    for ward_data in ward_requirements.values():
        totals['nurses_day'] += ward_data['nurses_day']
        totals['nurses_night'] += ward_data['nurses_night']
        totals['doctors'] += ward_data['doctors']
        totals['support_staff'] += ward_data['support_staff']
        totals['total_patients'] += ward_data['estimated_patients']
    
    return totals


def _analyze_current_staff(users: pd.DataFrame) -> Dict[str, Any]:
    """Analyze current staff composition"""
    if 'staff_type' not in users.columns:
        # If staff_type not available, create mock data
        staff_types = ['nurse', 'doctor', 'support', 'admin']
        users['staff_type'] = np.random.choice(staff_types, len(users))
    
    staff_counts = users['staff_type'].value_counts().to_dict()
    
    # Standardize staff type names
    standardized_counts = {
        'nurses': staff_counts.get('nurse', 0) + staff_counts.get('Nurse', 0),
        'doctors': staff_counts.get('doctor', 0) + staff_counts.get('Doctor', 0),
        'support_staff': (staff_counts.get('support', 0) + 
                         staff_counts.get('Support', 0) + 
                         staff_counts.get('technician', 0)),
        'admin_staff': staff_counts.get('admin', 0) + staff_counts.get('Admin', 0)
    }
    
    total_staff = sum(standardized_counts.values())
    
    return {
        'by_type': standardized_counts,
        'total_staff': total_staff,
        'analysis_date': pd.Timestamp.utcnow().strftime('%Y-%m-%d')
    }


def _generate_staffing_recommendations(forecast_data: list, current_staff: Dict) -> list:
    """Generate staffing recommendations based on forecast vs current staff"""
    recommendations = []
    
    # Get peak requirements from forecast
    peak_day_nurses = max([day['total_requirements']['nurses_day'] for day in forecast_data])
    peak_night_nurses = max([day['total_requirements']['nurses_night'] for day in forecast_data])
    peak_doctors = max([day['total_requirements']['doctors'] for day in forecast_data])
    peak_support = max([day['total_requirements']['support_staff'] for day in forecast_data])
    
    # Compare with current staff
    current_nurses = current_staff['by_type']['nurses']
    current_doctors = current_staff['by_type']['doctors']
    current_support = current_staff['by_type']['support_staff']
    
    # Nurse recommendations
    if peak_day_nurses > current_nurses:
        recommendations.append({
            'type': 'shortage',
            'staff_category': 'nurses',
            'current': current_nurses,
            'required': peak_day_nurses,
            'shortage': peak_day_nurses - current_nurses,
            'priority': 'high',
            'message': f'Nurse shortage: need {peak_day_nurses - current_nurses} additional nurses for day shifts'
        })
    elif current_nurses > peak_day_nurses * 1.2:
        recommendations.append({
            'type': 'surplus',
            'staff_category': 'nurses',
            'current': current_nurses,
            'required': peak_day_nurses,
            'surplus': current_nurses - peak_day_nurses,
            'priority': 'low',
            'message': f'Potential nurse surplus: {current_nurses - peak_day_nurses} nurses above forecast needs'
        })
    
    # Doctor recommendations
    if peak_doctors > current_doctors:
        recommendations.append({
            'type': 'shortage',
            'staff_category': 'doctors',
            'current': current_doctors,
            'required': peak_doctors,
            'shortage': peak_doctors - current_doctors,
            'priority': 'high',
            'message': f'Doctor shortage: need {peak_doctors - current_doctors} additional doctors'
        })
    
    # Support staff recommendations
    if peak_support > current_support:
        recommendations.append({
            'type': 'shortage',
            'staff_category': 'support_staff',
            'current': current_support,
            'required': peak_support,
            'shortage': peak_support - current_support,
            'priority': 'medium',
            'message': f'Support staff shortage: need {peak_support - current_support} additional support staff'
        })
    
    # General recommendations
    if not recommendations:
        recommendations.append({
            'type': 'adequate',
            'staff_category': 'all',
            'priority': 'low',
            'message': 'Current staffing levels appear adequate for forecast period'
        })
    
    return recommendations 