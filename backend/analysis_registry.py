"""
Unified analysis registry for Smart Hospital Dashboard.
Maps analysis functions to their configurations and chart types.
"""
from . import analytics
from .analytics import occupancy, census_forecast, admission_split, los_model, burn_rate, staffing


ANALYSES = {
    "bed_snapshot": {
        "label": "Real-time bed occupancy by ward",
        "fn": occupancy.get_bed_snapshot,
        "default_chart": "stacked_bar",
        "extra_charts": ["100pct_area", "bar"],
        "description": "Current bed utilization across all hospital wards",
        "category": "operational"
    },
    "census_forecast": {
        "label": "Short-horizon bed census forecast",
        "fn": census_forecast.forecast_bed_census,
        "default_chart": "line",
        "extra_charts": ["line_conf_band", "area"],
        "description": "3-day forecast of bed occupancy using time series analysis",
        "category": "predictive"
    },
    "admission_split": {
        "label": "Elective vs emergency demand split",
        "fn": admission_split.admission_split,
        "default_chart": "stacked_bar",
        "extra_charts": ["pie", "grouped_bar"],
        "description": "Analysis of admission patterns by type and time",
        "category": "operational"
    },
    "los_prediction": {
        "label": "Average length-of-stay analysis",
        "fn": los_model.los_summary,
        "default_chart": "bar_h",
        "extra_charts": ["box", "bar"],
        "description": "Length of stay statistics and predictions by ward",
        "category": "predictive"
    },
    "burn_rate": {
        "label": "Consumable burn-rate forecast",
        "fn": burn_rate.forecast_consumables,
        "default_chart": "stacked_area",
        "extra_charts": ["line", "bar"],
        "description": "Forecast of consumable usage and inventory depletion",
        "category": "predictive"
    },
    "staffing": {
        "label": "Staffing needs forecast",
        "fn": staffing.forecast_staff,
        "default_chart": "grouped_bar",
        "extra_charts": ["dual_axis_line", "stacked_bar"],
        "description": "Staffing requirement predictions based on occupancy",
        "category": "predictive"
    }
}


def get_analysis_list():
    """Get list of available analyses with metadata."""
    return [
        {
            "id": analysis_id,
            "label": config["label"],
            "description": config["description"],
            "category": config["category"],
            "default_chart": config["default_chart"],
            "extra_charts": config["extra_charts"]
        }
        for analysis_id, config in ANALYSES.items()
    ]


def get_analysis_by_category():
    """Get analyses grouped by category."""
    categories = {}
    for analysis_id, config in ANALYSES.items():
        category = config["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": analysis_id,
            "label": config["label"],
            "description": config["description"]
        })
    return categories


async def run_analysis(analysis_id: str, **kwargs):
    """
    Run a specific analysis by ID.
    
    Args:
        analysis_id: The ID of the analysis to run
        **kwargs: Additional parameters to pass to the analysis function
        
    Returns:
        Dictionary with analysis results and metadata
    """
    if analysis_id not in ANALYSES:
        return {
            "error": f"Unknown analysis ID: {analysis_id}",
            "available_analyses": list(ANALYSES.keys())
        }
    
    config = ANALYSES[analysis_id]
    
    try:
        # Run the analysis function
        data = config["fn"](**kwargs)
        
        return {
            "analysis_id": analysis_id,
            "label": config["label"],
            "default_chart": config["default_chart"],
            "extra_charts": config["extra_charts"],
            "category": config["category"],
            "data": data
        }
        
    except Exception as e:
        return {
            "error": f"Analysis '{analysis_id}' failed: {str(e)}",
            "analysis_id": analysis_id,
            "label": config["label"]
        } 