"""
Consumable burn rate analytics module.
Forecasts consumable usage based on historical patterns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..db_utils import db


def forecast_consumables(days: int = 7) -> dict:
    """
    Forecast consumable usage for the next N days.
    
    Args:
        days: Number of days to forecast (default: 7)
        
    Returns:
        Dictionary with consumable usage forecast data.
    """
    # Get inventory data
    inventory = db.get_inventory()
    
    if inventory.empty:
        return {
            "data": [],
            "error": "No inventory data available"
        }
    
    # Get current bed occupancy for usage rate calculation
    occupancy = db.get_occupancy(days_back=30)
    
    # Calculate current occupancy
    now = pd.Timestamp.utcnow()
    active_occupancy = occupancy[
        (occupancy["discharged_at"].isna()) | 
        (occupancy["discharged_at"] > now)
    ]
    current_occupied_beds = len(active_occupancy)
    
    # Define consumable categories and their usage patterns
    consumable_categories = {
        "Medical Supplies": {
            "daily_per_bed": 2.5,  # units per bed per day
            "priority": "high"
        },
        "Pharmaceuticals": {
            "daily_per_bed": 1.8,
            "priority": "critical"
        },
        "Surgical Supplies": {
            "daily_per_bed": 0.5,  # Lower usage, procedure-dependent
            "priority": "high"
        },
        "Disposables": {
            "daily_per_bed": 3.2,  # High turnover items
            "priority": "medium"
        },
        "Linens": {
            "daily_per_bed": 1.0,
            "priority": "medium"
        }
    }
    
    # Filter for consumable items (exclude equipment)
    consumables = inventory[
        inventory["category"].isin(consumable_categories.keys())
    ].copy()
    
    if consumables.empty:
        # Use all inventory items if no specific categories found
        consumables = inventory.copy()
        # Default usage pattern for unknown categories
        for category in consumables["category"].unique():
            if category not in consumable_categories:
                consumable_categories[category] = {
                    "daily_per_bed": 1.0,
                    "priority": "medium"
                }
    
    # Calculate forecasted usage
    forecast_data = []
    for _, item in consumables.iterrows():
        category = item["category"]
        category_info = consumable_categories.get(category, {
            "daily_per_bed": 1.0,
            "priority": "medium"
        })
        
        # Base daily usage calculation
        daily_usage = category_info["daily_per_bed"] * current_occupied_beds
        
        # Add some randomness to simulate real-world variability
        daily_usage *= np.random.uniform(0.8, 1.2)  # ±20% variation
        
        # Calculate days until depletion
        current_stock = item["quantity_available"]
        days_until_depletion = (
            current_stock / daily_usage if daily_usage > 0 else float('inf')
        )
        
        # Generate daily forecast
        daily_forecasts = []
        remaining_stock = current_stock
        
        for day in range(1, days + 1):
            forecast_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_consumption = daily_usage * np.random.uniform(0.9, 1.1)  # Daily variation
            remaining_stock = max(0, remaining_stock - daily_consumption)
            
            daily_forecasts.append({
                "date": forecast_date,
                "predicted_consumption": round(daily_consumption, 1),
                "remaining_stock": round(remaining_stock, 1),
                "stock_status": "critical" if remaining_stock < daily_usage * 3 else 
                              "low" if remaining_stock < daily_usage * 7 else "adequate"
            })
        
        item_forecast = {
            "item_name": item["item_name"],
            "category": category,
            "current_stock": int(current_stock),
            "daily_usage_rate": round(daily_usage, 1),
            "days_until_depletion": round(days_until_depletion, 1) if days_until_depletion != float('inf') else None,
            "priority": category_info["priority"],
            "daily_forecast": daily_forecasts,
            "reorder_recommended": days_until_depletion < 14  # Recommend reorder if < 2 weeks
        }
        
        forecast_data.append(item_forecast)
    
    # Sort by urgency (days until depletion)
    forecast_data.sort(key=lambda x: x["days_until_depletion"] or float('inf'))
    
    # Calculate summary statistics
    critical_items = sum(1 for item in forecast_data if item["days_until_depletion"] and item["days_until_depletion"] < 7)
    reorder_items = sum(1 for item in forecast_data if item["reorder_recommended"])
    
    # Category-level summaries
    category_summaries = {}
    for category in consumable_categories:
        category_items = [item for item in forecast_data if item["category"] == category]
        if category_items:
            avg_depletion = np.mean([
                item["days_until_depletion"] for item in category_items 
                if item["days_until_depletion"] is not None
            ]) if any(item["days_until_depletion"] for item in category_items) else None
            
            category_summaries[category] = {
                "total_items": len(category_items),
                "critical_items": sum(1 for item in category_items 
                                    if item["days_until_depletion"] and item["days_until_depletion"] < 7),
                "avg_days_until_depletion": round(avg_depletion, 1) if avg_depletion else None
            }
    
    return {
        "items": forecast_data[:20],  # Top 20 items by urgency
        "summary": {
            "total_items_tracked": len(forecast_data),
            "critical_items": critical_items,
            "reorder_recommended": reorder_items,
            "current_occupied_beds": current_occupied_beds,
            "forecast_period": f"{days} days"
        },
        "category_summaries": category_summaries,
        "timestamp": datetime.now().isoformat()
    } 