"""
Bed census forecasting using time series analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
from ..database import get_occupancy, get_rooms
from ..storage import save_analysis_result, save_model_data

warnings.filterwarnings("ignore", category=FutureWarning)


def forecast_bed_census(days: int = 3, save_results: bool = True) -> Dict[str, Any]:
    """
    Forecast bed census using Holt-Winters exponential smoothing
    
    Args:
        days: Number of days to forecast ahead
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with forecast data
    """
    # Load data
    occupancy = get_occupancy()
    rooms = get_rooms()
    
    # Clean data
    occupancy.drop(columns=[c for c in occupancy.columns if c.startswith("Unnamed")], 
                   inplace=True, errors="ignore")
    
    # Convert datetime columns to proper format
    if 'assigned_at' in occupancy.columns:
        occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
    if 'discharged_at' in occupancy.columns:
        occupancy['discharged_at'] = pd.to_datetime(occupancy['discharged_at'])
    
    # Build daily bed census series
    series_dates = []
    for _, row in occupancy.iterrows():
        start_date = row.assigned_at.normalize()
        end_date = (row.discharged_at.normalize() 
                   if pd.notnull(row.discharged_at) 
                   else pd.Timestamp.utcnow().tz_localize(None).normalize())
        
        # Only add if end_date is after start_date
        if end_date > start_date:
            date_range = pd.date_range(start_date, end_date, freq="D")
            series_dates.append(date_range)
    
    # Handle case where series_dates is empty
    if not series_dates:
        # Return default forecast with zeros
        forecast_dates = pd.date_range(
            pd.Timestamp.utcnow().tz_localize(None).normalize(), 
            periods=days, 
            freq="D"
        )
        result = {
            "forecast": [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_occupied_beds": 0,
                    "utilisation_pct": 0.0
                }
                for date in forecast_dates
            ],
            "historical_data": [],
            "model_info": {
                "method": "holt_winters",
                "forecast_days": days,
                "total_capacity": int(rooms.bed_capacity.sum())
            }
        }
        
        if save_results:
            save_analysis_result("census_forecast", result)
            model_data = {
                "analysis_type": "census_forecast",
                "method": "holt_winters",
                "forecast_days": days,
                "data_points": 0,
                "model_status": "no_data_available"
            }
            save_model_data("census_forecast", model_data)
        
        return result
    
    # Create bed census time series
    all_dates = pd.to_datetime(np.concatenate(series_dates))
    series = pd.Series(all_dates).value_counts().sort_index()
    series = series.asfreq("D", fill_value=0)
    
    # Ensure we have enough data for forecasting
    if len(series) < 3:
        # Pad with zeros if needed
        today = pd.Timestamp.utcnow().tz_localize(None).normalize()
        extended_index = pd.date_range(
            end=today, 
            periods=max(3, len(series)), 
            freq="D"
        )
        series = series.reindex(extended_index, fill_value=0)
    
    # Initialize model variables
    model_params = {}
    model_method = "holt_winters"
    
    # Fit Holt-Winters model
    try:
        model = ExponentialSmoothing(
            series, 
            initialization_method="estimated"
        ).fit()
        forecast = model.forecast(days)
        
        # Extract model parameters
        model_params = {
            "alpha": float(model.params.get('smoothing_level', 0)),
            "beta": float(model.params.get('smoothing_trend', 0)),
            "gamma": float(model.params.get('smoothing_seasonal', 0)),
            "l0": float(model.params.get('initial_level', 0)),
            "b0": float(model.params.get('initial_trend', 0)),
            "aic": float(model.aic) if hasattr(model, 'aic') else None,
            "aicc": float(model.aicc) if hasattr(model, 'aicc') else None,
            "bic": float(model.bic) if hasattr(model, 'bic') else None
        }
        
    except Exception as e:
        # Fallback to simple moving average if Holt-Winters fails
        model_method = "moving_average"
        mean_value = series.tail(7).mean()
        forecast = pd.Series(
            [mean_value] * days,
            index=pd.date_range(
                series.index[-1] + timedelta(days=1), 
                periods=days, 
                freq="D"
            )
        )
        
        model_params = {
            "method": "moving_average",
            "window_size": 7,
            "mean_value": float(mean_value),
            "error": str(e)
        }
    
    # Calculate total bed capacity
    total_capacity = rooms.bed_capacity.sum()
    
    # Prepare forecast data
    forecast_data = []
    for date, value in forecast.items():
        forecast_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "predicted_occupied_beds": max(0, int(round(value))),
            "utilisation_pct": float(round(max(0, value) / total_capacity * 100, 1))
        })
    
    # Prepare historical data (last 30 days)
    historical_data = []
    for date, value in series.tail(30).items():
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "occupied_beds": int(value),
            "utilisation_pct": float(round(value / total_capacity * 100, 1))
        })
    
    result = {
        "forecast": forecast_data,
        "historical_data": historical_data,
        "model_info": {
            "method": model_method,
            "forecast_days": days,
            "total_capacity": int(total_capacity),
            "historical_period_days": len(series)
        }
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data (JSON)
        save_analysis_result("census_forecast", result)
        
        # Force CSV generation
        save_analysis_result("census_forecast", result, format="csv")
        
        # Save model data with parameters
        model_data = {
            "analysis_type": "census_forecast",
            "method": model_method,
            "forecast_days": days,
            "data_points": len(series),
            "parameters": model_params,
            "series_stats": {
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "start_date": series.index[0].strftime("%Y-%m-%d"),
                "end_date": series.index[-1].strftime("%Y-%m-%d")
            },
            "model_accuracy": model_params
        }
        save_model_data("census_forecast", model_data)
    
    return result 