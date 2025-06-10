"""
Tool utilisation analytics
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from ..database import get_tools
from ..storage import save_analysis_result, save_model_data


def tool_utilisation_analysis(top_n: int = 10, save_results: bool = True) -> Dict[str, Any]:
    """
    Analyze tool utilisation rates and identify top utilized tools
    
    Args:
        top_n: Number of top tools to return
        save_results: Whether to save results to storage
        
    Returns:
        JSON-serializable dict with tool utilisation data
    """
    # Load data
    tools = get_tools()
    
    # Clean data
    tools.drop(columns=[c for c in tools.columns if c.startswith("Unnamed")], 
               inplace=True, errors="ignore")
    
    # Calculate utilisation percentage
    if "quantity_in_use" in tools.columns:
        # Primary method: use quantity_in_use
        tools["util_pct"] = (
            tools.quantity_in_use / tools.quantity_available
        ).clip(0, 1) * 100
        calculation_method = "quantity_in_use"
    elif "quantity_total" in tools.columns:
        # Fallback method: calculate from total vs available
        tools["util_pct"] = (
            (tools.quantity_total - tools.quantity_available) / tools.quantity_total
        ).clip(0, 1) * 100
        calculation_method = "total_minus_available"
    else:
        # Default method: assume 50% baseline utilisation
        tools["util_pct"] = 50.0
        calculation_method = "default_baseline"
    
    # Round utilisation percentages
    tools["util_pct"] = tools["util_pct"].round(1)
    
    # Get top N tools by utilisation
    top_tools = tools.sort_values("util_pct", ascending=False).head(top_n)
    
    # Prepare tool data
    tool_data = []
    for _, tool in top_tools.iterrows():
        tool_data.append({
            "tool_name": tool.get("tool_name", "Unknown Tool"),
            "util_pct": float(tool["util_pct"]),
            "quantity_available": int(tool.get("quantity_available", 0)),
            "quantity_in_use": int(tool.get("quantity_in_use", 0)) if "quantity_in_use" in tools.columns else None,
            "quantity_total": int(tool.get("quantity_total", 0)) if "quantity_total" in tools.columns else None,
            "category": tool.get("category", "General"),
            "status": _get_utilisation_status(tool["util_pct"])
        })
    
    # Calculate summary statistics
    summary_stats = {
        "total_tools": len(tools),
        "avg_utilisation": float(tools["util_pct"].mean().round(1)),
        "median_utilisation": float(tools["util_pct"].median().round(1)),
        "max_utilisation": float(tools["util_pct"].max().round(1)),
        "min_utilisation": float(tools["util_pct"].min().round(1)),
        "high_util_tools": int((tools["util_pct"] > 80).sum()),
        "medium_util_tools": int(tools["util_pct"].between(40, 80).sum()),
        "low_util_tools": int((tools["util_pct"] < 40).sum())
    }
    
    # Utilisation distribution
    util_distribution = []
    for range_name, (min_val, max_val) in [
        ("Critical (90-100%)", (90, 100)),
        ("High (80-90%)", (80, 90)),
        ("Medium (40-80%)", (40, 80)),
        ("Low (0-40%)", (0, 40))
    ]:
        count = int(tools["util_pct"].between(min_val, max_val).sum())
        util_distribution.append({
            "range": range_name,
            "count": count,
            "percentage": float(round(count / len(tools) * 100, 1))
        })
    
    result = {
        "top_tools": tool_data,
        "summary_statistics": summary_stats,
        "utilisation_distribution": util_distribution,
        "calculation_method": calculation_method,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Save results and model data if requested
    if save_results:
        # Save the result data
        save_analysis_result("tool_utilisation", result)
        
        # Also save as CSV for tabular data
        if tool_data:
            tools_df = pd.DataFrame(tool_data)
            save_analysis_result("tool_utilisation", {"tools_data": tools_df.to_dict('records')}, format="csv")
        
        # Save model/analysis data
        model_data = {
            "analysis_type": "tool_utilisation",
            "calculation_method": calculation_method,
            "top_n_analyzed": top_n,
            "utilisation_formula": _get_formula_description(calculation_method),
            "status_thresholds": {
                "critical": "90-100%",
                "high": "80-90%", 
                "medium": "40-80%",
                "low": "0-40%"
            },
            "data_quality": {
                "total_tools_analyzed": len(tools),
                "has_quantity_in_use": "quantity_in_use" in tools.columns,
                "has_quantity_total": "quantity_total" in tools.columns,
                "calculation_reliability": _get_reliability_score(calculation_method)
            },
            "summary_insights": summary_stats
        }
        save_model_data("tool_utilisation", model_data)
    
    return result


def _get_utilisation_status(util_pct: float) -> str:
    """Determine utilisation status based on percentage"""
    if util_pct >= 90:
        return "critical"
    elif util_pct >= 80:
        return "high"
    elif util_pct >= 40:
        return "medium"
    else:
        return "low"


def _get_formula_description(method: str) -> str:
    """Get description of calculation formula"""
    if method == "quantity_in_use":
        return "quantity_in_use / quantity_available * 100"
    elif method == "total_minus_available":
        return "(quantity_total - quantity_available) / quantity_total * 100"
    else:
        return "default baseline of 50%"


def _get_reliability_score(method: str) -> str:
    """Get reliability score for calculation method"""
    if method == "quantity_in_use":
        return "high"
    elif method == "total_minus_available":
        return "medium"
    else:
        return "low" 