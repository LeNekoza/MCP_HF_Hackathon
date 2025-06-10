"""
Consumable burn rate analytics and forecasting
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from ..database import get_inventory
from ..storage import save_analysis_result, save_model_data


def forecast_consumables(days: int = 7, save_results: bool = True) -> Dict[str, Any]:
    """
    Forecast consumable usage and identify items needing restocking
    
    Args:
        days: Number of days to forecast ahead
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with burn rate forecast data
    """
    # Load inventory data
    inventory = get_inventory()
    
    # Clean data
    inventory.drop(columns=[c for c in inventory.columns if c.startswith("Unnamed")], 
                   inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'expiry_date' in inventory.columns:
        inventory['expiry_date'] = pd.to_datetime(inventory['expiry_date'])
    
    # Calculate days to expiry
    current_date = pd.Timestamp.utcnow().tz_localize(None).normalize()
    inventory['days_to_expiry'] = (inventory['expiry_date'] - current_date).dt.days
    
    # Simulate daily usage rates based on item type and current stock levels
    # In a real system, this would be based on historical usage data
    inventory['daily_usage_rate'] = _estimate_daily_usage(inventory)
    
    # Calculate forecasted usage over the forecast period
    inventory['forecasted_usage'] = inventory['daily_usage_rate'] * days
    inventory['remaining_after_forecast'] = (
        inventory['quantity_available'] - inventory['forecasted_usage']
    ).clip(lower=0)
    
    # Identify items that will be depleted
    critical_items = inventory[
        inventory['remaining_after_forecast'] <= 0
    ].copy()
    
    # Items expiring soon (within forecast period)
    expiring_items = inventory[
        (inventory['days_to_expiry'] <= days) & 
        (inventory['days_to_expiry'] > 0)
    ].copy()
    
    # Items needing restocking (low stock or high usage)
    restock_threshold = inventory['quantity_available'] * 0.2  # 20% threshold
    low_stock_items = inventory[
        inventory['quantity_available'] <= restock_threshold
    ].copy()
    
    # Prepare forecast data
    forecast_items = []
    for _, item in inventory.iterrows():
        forecast_items.append({
            'item_name': item['item_name'],
            'current_stock': int(item['quantity_available']),
            'daily_usage_rate': float(round(item['daily_usage_rate'], 2)),
            'forecasted_usage': float(round(item['forecasted_usage'], 2)),
            'remaining_after_forecast': int(round(item['remaining_after_forecast'])),
            'days_to_expiry': int(item['days_to_expiry']) if pd.notnull(item['days_to_expiry']) else None,
            'status': _get_item_status(item, days)
        })
    
    # Sort by priority (critical items first)
    forecast_items.sort(key=lambda x: (
        x['status'] == 'critical',
        x['status'] == 'low_stock',
        x['status'] == 'expiring_soon'
    ), reverse=True)
    
    # Summary statistics
    total_items = len(inventory)
    critical_count = len(critical_items)
    expiring_count = len(expiring_items)
    low_stock_count = len(low_stock_items)
    
    result = {
        'forecast_period_days': days,
        'forecast_date': current_date.strftime('%Y-%m-%d'),
        'items': forecast_items,
        'summary': {
            'total_items': total_items,
            'critical_items': critical_count,
            'expiring_items': expiring_count,
            'low_stock_items': low_stock_count,
            'items_needing_attention': critical_count + expiring_count + low_stock_count
        },
        'alerts': _generate_alerts(critical_items, expiring_items, low_stock_items)
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data (JSON)
        save_analysis_result("burn_rate", result)
        
        # Also save as CSV for tabular data
        if result["items"]:
            save_analysis_result("burn_rate", {"items": result["items"]}, format="csv")
        
        # Save model/forecasting data
        model_data = {
            "analysis_type": "burn_rate",
            "forecast_parameters": {
                "forecast_days": days,
                "usage_estimation_method": "item_type_based",
                "restock_threshold_pct": 20,
                "expiry_warning_days": days
            },
            "usage_rate_model": {
                "high_usage_items": ["syringe", "needle", "glove"],
                "medium_usage_items": ["bandage", "gauze", "tape"],
                "moderate_usage_items": ["medication", "drug", "tablet"],
                "low_usage_items": ["equipment", "device", "monitor"],
                "base_rates": {
                    "high_usage": 5.0,
                    "medium_usage": 3.0,
                    "moderate_usage": 2.0,
                    "low_usage": 0.1,
                    "default": 0.5
                }
            },
            "status_thresholds": {
                "critical": "remaining_after_forecast <= 0",
                "low_stock": "quantity <= 20% of current",
                "expiring_soon": "days_to_expiry <= forecast_days",
                "watch": "remaining_after_forecast <= 30% of current"
            },
            "forecast_quality": {
                "total_items_analyzed": total_items,
                "items_with_expiry_dates": int(inventory['expiry_date'].notna().sum()),
                "average_daily_usage": float(inventory['daily_usage_rate'].mean()),
                "total_forecasted_consumption": float(inventory['forecasted_usage'].sum())
            }
        }
        save_model_data("burn_rate", model_data)
    
    return result


def _estimate_daily_usage(inventory: pd.DataFrame) -> pd.Series:
    """
    Estimate daily usage rates for inventory items
    This is a simplified model - in practice would use historical data
    """
    usage_rates = []
    
    for _, item in inventory.iterrows():
        item_name = item['item_name'].lower()
        base_rate = 0.5  # Default 0.5 units per day
        
        # Adjust based on item type
        if any(keyword in item_name for keyword in ['syringe', 'needle', 'glove']):
            base_rate = 5.0  # High usage items
        elif any(keyword in item_name for keyword in ['bandage', 'gauze', 'tape']):
            base_rate = 3.0  # Medium usage items
        elif any(keyword in item_name for keyword in ['medication', 'drug', 'tablet']):
            base_rate = 2.0  # Moderate usage
        elif any(keyword in item_name for keyword in ['equipment', 'device', 'monitor']):
            base_rate = 0.1  # Low usage equipment
        
        # Add some randomness to simulate real usage patterns
        variation = np.random.normal(1.0, 0.2)
        usage_rate = base_rate * max(0.1, variation)
        
        # Scale by current stock level (higher stock might indicate higher usage)
        stock_factor = min(2.0, item['quantity_available'] / 100)
        usage_rate *= stock_factor
        
        usage_rates.append(usage_rate)
    
    return pd.Series(usage_rates)


def _get_item_status(item: pd.Series, forecast_days: int) -> str:
    """Determine the status of an inventory item"""
    if item['remaining_after_forecast'] <= 0:
        return 'critical'
    elif item['quantity_available'] <= item['quantity_available'] * 0.2:
        return 'low_stock'
    elif pd.notnull(item['days_to_expiry']) and item['days_to_expiry'] <= forecast_days:
        return 'expiring_soon'
    elif item['remaining_after_forecast'] <= item['quantity_available'] * 0.3:
        return 'watch'
    else:
        return 'normal'


def _generate_alerts(critical_items: pd.DataFrame, expiring_items: pd.DataFrame, 
                    low_stock_items: pd.DataFrame) -> list:
    """Generate alert messages for inventory issues"""
    alerts = []
    
    if len(critical_items) > 0:
        alerts.append({
            'level': 'critical',
            'message': f'{len(critical_items)} items will be depleted within forecast period',
            'action': 'Immediate restocking required'
        })
    
    if len(expiring_items) > 0:
        alerts.append({
            'level': 'warning',
            'message': f'{len(expiring_items)} items expiring soon',
            'action': 'Review expiry dates and usage plans'
        })
    
    if len(low_stock_items) > 0:
        alerts.append({
            'level': 'info',
            'message': f'{len(low_stock_items)} items below restock threshold',
            'action': 'Consider ordering additional stock'
        })
    
    return alerts 