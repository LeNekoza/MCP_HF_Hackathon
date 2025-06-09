"""
Bed census forecasting module.
Provides short-horizon bed census predictions using Holt-Winters method.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from ..db_utils import db


def forecast_bed_census(days: int = 3) -> dict:
    """
    Forecast bed census for the next N days using Holt-Winters exponential smoothing.
    
    Args:
        days: Number of days to forecast (default: 3)
        
    Returns:
        Dictionary with historical and forecasted bed census data.
    """
    # Get occupancy data for the past 60 days
    occupancy = db.get_occupancy(days_back=60)
    
    # Build daily bed census time series
    series_dates = []
    for _, row in occupancy.iterrows():
        start_date = row["assigned_at"].normalize()
        end_date = (
            row["discharged_at"].normalize() 
            if pd.notnull(row["discharged_at"]) 
            else pd.Timestamp.utcnow().normalize()
        )
        
        # Skip invalid date ranges
        if pd.isna(start_date) or pd.isna(end_date):
            continue
            
        date_range = pd.date_range(start_date, end_date, freq="D")
        series_dates.extend(date_range)
    
    # Create time series of daily bed occupancy counts
    if not series_dates:
        # Fallback data if no valid dates
        return {
            "data": [],
            "forecast": [],
            "error": "No valid occupancy data found for forecasting"
        }
    
    series = pd.Series(series_dates).value_counts().sort_index()
    series = series.asfreq("D", fill_value=0)
    
    # Ensure we have enough data points for forecasting
    if len(series) < 7:
        # Return basic trend if insufficient data
        recent_avg = series.tail(3).mean() if len(series) > 0 else 0
        forecast_dates = [
            (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") 
            for i in range(1, days + 1)
        ]
        forecast_data = [{"date": date, "predicted": recent_avg} for date in forecast_dates]
        
        return {
            "data": [
                {"date": date.strftime("%Y-%m-%d"), "actual": int(count)}
                for date, count in series.tail(14).items()
            ],
            "forecast": forecast_data,
            "model": "simple_average"
        }
    
    try:
        # Fit Holt-Winters exponential smoothing
        model = ExponentialSmoothing(
            series, 
            initialization_method="estimated"
        ).fit()
        
        # Generate forecast
        forecast = model.forecast(days)
        
        # Format historical data (last 14 days)
        historical_data = [
            {"date": date.strftime("%Y-%m-%d"), "actual": int(count)}
            for date, count in series.tail(14).items()
        ]
        
        # Format forecast data
        forecast_dates = [
            datetime.now() + timedelta(days=i) for i in range(1, days + 1)
        ]
        forecast_data = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "predicted": round(float(pred), 1)
            }
            for date, pred in zip(forecast_dates, forecast)
        ]
        
        # Calculate confidence intervals (simple approximation)
        forecast_std = series.std()
        for item in forecast_data:
            item["confidence_lower"] = max(0, item["predicted"] - 1.96 * forecast_std)
            item["confidence_upper"] = item["predicted"] + 1.96 * forecast_std
        
        return {
            "data": historical_data,
            "forecast": forecast_data,
            "model": "holt_winters",
            "forecast_period": f"{days} days",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Fallback to simple average if model fails
        recent_avg = series.tail(7).mean()
        forecast_dates = [
            (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") 
            for i in range(1, days + 1)
        ]
        forecast_data = [
            {"date": date, "predicted": round(recent_avg, 1)}
            for date in forecast_dates
        ]
        
        return {
            "data": [
                {"date": date.strftime("%Y-%m-%d"), "actual": int(count)}
                for date, count in series.tail(14).items()
            ],
            "forecast": forecast_data,
            "model": "fallback_average",
            "error": str(e)
        } 