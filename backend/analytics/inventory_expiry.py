"""
Inventory expiry analytics
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from ..database import get_inventory
from ..storage import save_analysis_result, save_model_data


def inventory_expiry_analysis(days_threshold: int = 90, save_results: bool = True) -> Dict[str, Any]:
    """
    Analyze inventory items expiring within threshold period
    
    Args:
        days_threshold: Number of days ahead to check for expiry
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with inventory expiry data
    """
    # Load data
    inventory = get_inventory()
    
    # Clean data
    inventory.drop(columns=[c for c in inventory.columns if c.startswith("Unnamed")], 
                   inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'expiry_date' in inventory.columns:
        inventory['expiry_date'] = pd.to_datetime(inventory['expiry_date'])
    
    # Calculate days to expiry
    current_date = pd.Timestamp.utcnow().tz_localize(None)
    inventory['days_to_expiry'] = (inventory['expiry_date'] - current_date).dt.days
    
    # Filter items expiring within threshold
    expiring_soon = inventory[
        inventory['days_to_expiry'].between(0, days_threshold)
    ].sort_values('days_to_expiry')
    
    # Categorize by urgency
    expired_items = inventory[inventory['days_to_expiry'] < 0]
    critical_items = inventory[inventory['days_to_expiry'].between(0, 7)]  # 1 week
    urgent_items = inventory[inventory['days_to_expiry'].between(8, 30)]   # 1 month
    watch_items = inventory[inventory['days_to_expiry'].between(31, days_threshold)]  # up to threshold
    
    # Prepare expiring items data
    expiring_data = []
    for _, item in expiring_soon.iterrows():
        expiring_data.append({
            "item_name": item.get("item_name", "Unknown Item"),
            "days_to_expiry": int(item['days_to_expiry']),
            "expiry_date": item['expiry_date'].strftime('%Y-%m-%d') if pd.notnull(item['expiry_date']) else None,
            "quantity_available": int(item.get("quantity_available", 0)),
            "category": item.get("category", "General"),
            "urgency": _get_expiry_urgency(item['days_to_expiry']),
            "estimated_value": float(item.get("unit_cost", 0) * item.get("quantity_available", 0)) if 'unit_cost' in item else None
        })
    
    # Summary statistics
    summary_stats = {
        "total_inventory_items": len(inventory),
        "items_expiring_within_threshold": len(expiring_soon),
        "expired_items": len(expired_items),
        "critical_items": len(critical_items),
        "urgent_items": len(urgent_items),
        "watch_items": len(watch_items),
        "percentage_expiring": float(round(len(expiring_soon) / len(inventory) * 100, 1)) if len(inventory) > 0 else 0.0
    }
    
    # Category breakdown
    category_breakdown = []
    if 'category' in inventory.columns:
        for category in inventory['category'].unique():
            cat_items = expiring_soon[expiring_soon['category'] == category]
            category_breakdown.append({
                "category": category,
                "items_expiring": len(cat_items),
                "total_quantity": int(cat_items['quantity_available'].sum()),
                "avg_days_to_expiry": float(cat_items['days_to_expiry'].mean().round(1)) if len(cat_items) > 0 else 0
            })
    
    # Value at risk (if cost data available)
    value_at_risk = 0.0
    if 'unit_cost' in inventory.columns:
        expiring_soon['total_value'] = expiring_soon['unit_cost'] * expiring_soon['quantity_available']
        value_at_risk = float(expiring_soon['total_value'].sum())
    
    # Generate alerts
    alerts = _generate_expiry_alerts(expired_items, critical_items, urgent_items)
    
    result = {
        "expiring_items": expiring_data,
        "summary_statistics": summary_stats,
        "category_breakdown": category_breakdown,
        "value_at_risk": value_at_risk,
        "alerts": alerts,
        "analysis_parameters": {
            "days_threshold": days_threshold,
            "analysis_date": current_date.strftime('%Y-%m-%d')
        },
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data
        save_analysis_result("inventory_expiry", result)
        
        # Also save as CSV for tabular data
        if expiring_data:
            expiry_df = pd.DataFrame(expiring_data)
            save_analysis_result("inventory_expiry", {"expiring_items": expiry_df.to_dict('records')}, format="csv")
        
        # Save model/analysis data
        model_data = {
            "analysis_type": "inventory_expiry",
            "days_threshold": days_threshold,
            "urgency_categories": {
                "expired": "< 0 days",
                "critical": "0-7 days",
                "urgent": "8-30 days", 
                "watch": f"31-{days_threshold} days"
            },
            "calculation_method": "days_to_expiry = expiry_date - current_date",
            "data_quality": {
                "total_inventory_items": len(inventory),
                "items_with_expiry_dates": int(inventory['expiry_date'].notna().sum()),
                "has_cost_data": 'unit_cost' in inventory.columns,
                "has_category_data": 'category' in inventory.columns
            },
            "risk_assessment": {
                "items_at_risk": len(expiring_soon),
                "percentage_at_risk": summary_stats["percentage_expiring"],
                "value_at_risk": value_at_risk,
                "alert_count": len(alerts)
            }
        }
        save_model_data("inventory_expiry", model_data)
    
    return result


def _get_expiry_urgency(days_to_expiry: int) -> str:
    """Determine urgency level based on days to expiry"""
    if days_to_expiry < 0:
        return "expired"
    elif days_to_expiry <= 7:
        return "critical"
    elif days_to_expiry <= 30:
        return "urgent"
    else:
        return "watch"


def _generate_expiry_alerts(expired_items: pd.DataFrame, critical_items: pd.DataFrame, 
                           urgent_items: pd.DataFrame) -> list:
    """Generate alert messages for inventory expiry issues"""
    alerts = []
    
    if len(expired_items) > 0:
        alerts.append({
            'level': 'critical',
            'message': f'{len(expired_items)} items have already expired',
            'action': 'Immediate removal and disposal required',
            'count': len(expired_items)
        })
    
    if len(critical_items) > 0:
        alerts.append({
            'level': 'critical',
            'message': f'{len(critical_items)} items expiring within 7 days',
            'action': 'Urgent review and usage planning required',
            'count': len(critical_items)
        })
    
    if len(urgent_items) > 0:
        alerts.append({
            'level': 'warning',
            'message': f'{len(urgent_items)} items expiring within 30 days',
            'action': 'Schedule usage or consider redistribution',
            'count': len(urgent_items)
        })
    
    if len(alerts) == 0:
        alerts.append({
            'level': 'info',
            'message': 'No immediate expiry concerns detected',
            'action': 'Continue regular monitoring',
            'count': 0
        })
    
    return alerts 