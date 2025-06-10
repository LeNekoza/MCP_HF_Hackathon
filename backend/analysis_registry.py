"""
Unified Analysis Registry for Smart Hospital Analytics

This module provides a centralized registry of all available analytics,
their metadata, and a unified API endpoint for data retrieval.
"""
from typing import Dict, Any, Callable
import logging
from .analytics import occupancy, census_forecast, admission_split, los_model, burn_rate, staffing

logger = logging.getLogger(__name__)

# Analytics registry mapping analysis IDs to their metadata and functions
ANALYSES: Dict[str, Dict[str, Any]] = {
    "bed_snapshot": {
        "label": "Real-time bed occupancy by ward",
        "description": "Current bed utilization across all hospital wards with capacity analysis",
        "fn": occupancy.get_bed_snapshot,
        "default_chart": "stacked_bar",
        "extra_charts": ["100pct_area", "pie"],
        "category": "operational",
        "refresh_interval": 300,  # 5 minutes
        "parameters": {
            "date": {"type": "datetime", "optional": True, "description": "Snapshot date"}
        }
    },
    "census_forecast": {
        "label": "Short-horizon bed census forecast",
        "description": "3-day bed census prediction using time series analysis",
        "fn": census_forecast.forecast_bed_census,
        "default_chart": "line",
        "extra_charts": ["line_conf_band", "area"],
        "category": "predictive",
        "refresh_interval": 3600,  # 1 hour
        "parameters": {
            "days": {"type": "int", "optional": True, "default": 3, "min": 1, "max": 7}
        }
    },
    "admission_split": {
        "label": "Elective vs emergency demand split",
        "description": "Analysis of admission patterns by type and timing",
        "fn": admission_split.admission_split,
        "default_chart": "stacked_bar",
        "extra_charts": ["pie", "line", "stacked_area"],
        "category": "operational",
        "refresh_interval": 1800,  # 30 minutes
        "parameters": {
            "days_back": {"type": "int", "optional": True, "default": 14, "min": 1, "max": 90}
        }
    },
    "los_prediction": {
        "label": "Length of stay analytics",
        "description": "Average length of stay statistics and predictions by ward",
        "fn": los_model.los_summary,
        "default_chart": "bar_h",
        "extra_charts": ["box", "violin"],
        "category": "predictive",
        "refresh_interval": 7200,  # 2 hours
        "parameters": {}
    },
    "burn_rate": {
        "label": "Consumable burn rate forecast",
        "description": "Inventory usage prediction and restocking recommendations",
        "fn": burn_rate.forecast_consumables,
        "default_chart": "stacked_area",
        "extra_charts": ["bar", "table"],
        "category": "operational",
        "refresh_interval": 3600,  # 1 hour
        "parameters": {
            "days": {"type": "int", "optional": True, "default": 7, "min": 1, "max": 30}
        }
    },
    "staffing": {
        "label": "Staffing requirements forecast",
        "description": "Staff allocation predictions based on patient load",
        "fn": staffing.forecast_staff,
        "default_chart": "grouped_bar",
        "extra_charts": ["dual_axis_line", "stacked_bar"],
        "category": "operational",
        "refresh_interval": 1800,  # 30 minutes
        "parameters": {
            "days": {"type": "int", "optional": True, "default": 3, "min": 1, "max": 7}
        }
    }
}


def get_analysis_metadata() -> Dict[str, Any]:
    """
    Get metadata for all available analyses
    
    Returns:
        Dict with analysis metadata (without function references)
    """
    metadata = {}
    for analysis_id, config in ANALYSES.items():
        metadata[analysis_id] = {
            key: value for key, value in config.items() 
            if key != "fn"  # Exclude function reference
        }
    return metadata


def get_analysis_list() -> list:
    """
    Get a list of available analyses with basic info
    
    Returns:
        List of dicts with analysis ID, label, and category
    """
    return [
        {
            "id": analysis_id,
            "label": config["label"],
            "category": config["category"],
            "description": config["description"]
        }
        for analysis_id, config in ANALYSES.items()
    ]


def execute_analysis(analysis_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a specific analysis with optional parameters
    
    Args:
        analysis_id: The analysis to execute
        parameters: Optional parameters for the analysis function
        
    Returns:
        Analysis results with metadata
    """
    if analysis_id not in ANALYSES:
        raise ValueError(f"Unknown analysis ID: {analysis_id}")
    
    config = ANALYSES[analysis_id]
    analysis_function = config["fn"]
    
    try:
        # Prepare parameters
        if parameters is None:
            parameters = {}
        
        # Validate and apply defaults
        validated_params = _validate_parameters(analysis_id, parameters)
        
        # Execute analysis
        logger.info(f"Executing analysis: {analysis_id} with params: {validated_params}")
        data = analysis_function(**validated_params)
        
        # Return results with metadata
        return {
            "analysis_id": analysis_id,
            "analysis_metadata": {
                "label": config["label"],
                "description": config["description"],
                "category": config["category"],
                "default_chart": config["default_chart"],
                "extra_charts": config["extra_charts"]
            },
            "parameters_used": validated_params,
            "data": data,
            "success": True,
            "timestamp": _get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error executing analysis {analysis_id}: {str(e)}")
        return {
            "analysis_id": analysis_id,
            "success": False,
            "error": str(e),
            "timestamp": _get_current_timestamp()
        }


def get_chart_options(analysis_id: str) -> Dict[str, Any]:
    """
    Get available chart types for a specific analysis
    
    Args:
        analysis_id: The analysis ID
        
    Returns:
        Dict with default chart and available options
    """
    if analysis_id not in ANALYSES:
        raise ValueError(f"Unknown analysis ID: {analysis_id}")
    
    config = ANALYSES[analysis_id]
    
    all_charts = [config["default_chart"]] + config["extra_charts"]
    
    return {
        "default_chart": config["default_chart"],
        "available_charts": all_charts,
        "chart_metadata": _get_chart_metadata(all_charts)
    }


def _validate_parameters(analysis_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and prepare parameters for analysis execution"""
    config = ANALYSES[analysis_id]
    param_specs = config.get("parameters", {})
    validated = {}
    
    for param_name, param_config in param_specs.items():
        if param_name in parameters:
            value = parameters[param_name]
            
            # Type validation
            expected_type = param_config["type"]
            if expected_type == "int" and not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Parameter {param_name} must be an integer")
            
            # Range validation
            if "min" in param_config and value < param_config["min"]:
                raise ValueError(f"Parameter {param_name} must be >= {param_config['min']}")
            if "max" in param_config and value > param_config["max"]:
                raise ValueError(f"Parameter {param_name} must be <= {param_config['max']}")
            
            validated[param_name] = value
            
        elif not param_config.get("optional", False):
            raise ValueError(f"Required parameter {param_name} not provided")
        elif "default" in param_config:
            validated[param_name] = param_config["default"]
    
    return validated


def _get_chart_metadata(chart_types: list) -> Dict[str, Dict[str, str]]:
    """Get metadata for chart types"""
    chart_info = {
        "line": {"name": "Line Chart", "type": "temporal", "best_for": "trends_over_time"},
        "bar": {"name": "Bar Chart", "type": "categorical", "best_for": "comparisons"},
        "bar_h": {"name": "Horizontal Bar", "type": "categorical", "best_for": "category_comparison"},
        "stacked_bar": {"name": "Stacked Bar", "type": "categorical", "best_for": "part_to_whole"},
        "grouped_bar": {"name": "Grouped Bar", "type": "categorical", "best_for": "multi_series_comparison"},
        "pie": {"name": "Pie Chart", "type": "categorical", "best_for": "proportions"},
        "area": {"name": "Area Chart", "type": "temporal", "best_for": "volume_over_time"},
        "stacked_area": {"name": "Stacked Area", "type": "temporal", "best_for": "cumulative_trends"},
        "100pct_area": {"name": "100% Stacked Area", "type": "temporal", "best_for": "proportion_trends"},
        "line_conf_band": {"name": "Line with Confidence", "type": "temporal", "best_for": "forecasts_uncertainty"},
        "dual_axis_line": {"name": "Dual Axis Line", "type": "temporal", "best_for": "different_scales"},
        "box": {"name": "Box Plot", "type": "statistical", "best_for": "distribution_analysis"},
        "violin": {"name": "Violin Plot", "type": "statistical", "best_for": "distribution_density"},
        "table": {"name": "Data Table", "type": "tabular", "best_for": "detailed_data"}
    }
    
    return {chart_type: chart_info.get(chart_type, {"name": chart_type.title(), "type": "unknown"}) 
            for chart_type in chart_types}


def _get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


# API function for external use
def get_analysis(analysis_id: str, **kwargs) -> Dict[str, Any]:
    """
    Main API function for getting analysis data
    
    Args:
        analysis_id: The analysis to execute
        **kwargs: Parameters to pass to the analysis function
        
    Returns:
        Complete analysis result with metadata
    """
    return execute_analysis(analysis_id, kwargs) 