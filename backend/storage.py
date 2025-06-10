"""
Storage utilities for saving analysis results and models
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Base directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(BACKEND_DIR, "result")
MODEL_DIR = os.path.join(BACKEND_DIR, "models")

# Ensure directories exist
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def save_analysis_result(analysis_id: str, data: Dict[str, Any], format: str = "json") -> str:
    """
    Save analysis result data to the result folder
    
    Args:
        analysis_id: The analysis identifier
        data: The result data to save
        format: File format ('json' or 'csv')
        
    Returns:
        Path to the saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        filename = f"{analysis_id}_result.json"
        filepath = os.path.join(RESULT_DIR, filename)
        
        # Add metadata
        result_with_metadata = {
            "analysis_id": analysis_id,
            "timestamp": timestamp,
            "generated_at": datetime.now().isoformat(),
            "data": data
        }
        
        with open(filepath, 'w') as f:
            json.dump(result_with_metadata, f, indent=2, default=str)
            
    elif format == "csv":
        filename = f"{analysis_id}_result.csv"
        filepath = os.path.join(RESULT_DIR, filename)
        
        # Enhanced CSV extraction logic
        try:
            df = None
            
            # Try different data extraction methods
            if isinstance(data, dict):
                # Method 1: Direct extraction from known keys
                extraction_map = {
                    'ward_data': 'wards',
                    'tools_data': 'top_tools', 
                    'expiring_items': 'expiring_items',
                    'staff_data': 'top_staff',
                    'items': 'items',
                    'forecast': 'forecast',
                    'ward_statistics': 'ward_statistics',
                    'daily_breakdown': 'daily_breakdown',
                    'overall_split': 'overall_split',
                    'daily_forecast': 'daily_forecast',
                    'current_staff_breakdown': 'current_staff_breakdown',
                    'wards': 'wards'
                }
                
                # Look for direct list data
                for key in extraction_map.keys():
                    if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                        df = pd.DataFrame(data[key])
                        break
                
                # Method 2: Look for nested data structure
                if df is None and 'data' in data:
                    nested_data = data['data']
                    if isinstance(nested_data, dict):
                        # Try to find the main tabular data in nested structure
                        for search_key in extraction_map.values():
                            if search_key in nested_data and isinstance(nested_data[search_key], list) and len(nested_data[search_key]) > 0:
                                df = pd.DataFrame(nested_data[search_key])
                                break
                    elif isinstance(nested_data, list) and len(nested_data) > 0:
                        df = pd.DataFrame(nested_data)
                
                # Method 3: Force CSV creation for specific analyses
                if df is None:
                    df = _force_csv_creation(analysis_id, data)
                
                # Method 4: Direct conversion if it's a flat structure
                if df is None and all(isinstance(v, (str, int, float, bool, type(None))) for v in data.values()):
                    df = pd.DataFrame([data])
            
            elif isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
            
            if df is not None and len(df) > 0:
                # Add metadata columns
                df['analysis_id'] = analysis_id
                df['generated_at'] = datetime.now().isoformat()
                df.to_csv(filepath, index=False)
            else:
                # If we still can't create CSV, create a summary CSV
                logger.warning(f"Could not extract tabular data for {analysis_id}, creating summary CSV")
                summary_df = _create_summary_csv(analysis_id, data)
                summary_df.to_csv(filepath, index=False)
                
        except Exception as e:
            logger.warning(f"Could not save as CSV, creating summary CSV instead: {e}")
            summary_df = _create_summary_csv(analysis_id, data)
            summary_df.to_csv(filepath, index=False)
    
    logger.info(f"Saved analysis result for {analysis_id} to {filepath}")
    return filepath


def _force_csv_creation(analysis_id: str, data: Dict[str, Any]) -> pd.DataFrame:
    """Force CSV creation for specific analyses that don't have obvious tabular data"""
    try:
        if analysis_id == "bed_snapshot":
            # Extract ward data or create summary
            if 'wards' in data and data['wards']:
                return pd.DataFrame(data['wards'])
            elif 'summary' in data:
                summary = data['summary']
                return pd.DataFrame([{
                    'metric': k,
                    'value': v,
                    'timestamp': data.get('timestamp', '')
                } for k, v in summary.items()])
        
        elif analysis_id == "census_forecast":
            # Extract forecast data
            if 'forecast' in data and data['forecast']:
                return pd.DataFrame(data['forecast'])
            elif 'model_info' in data:
                model_info = data['model_info']
                return pd.DataFrame([{
                    'metric': k,
                    'value': v
                } for k, v in model_info.items()])
        
        elif analysis_id == "admission_split":
            # Extract daily breakdown or overall split
            if 'daily_breakdown' in data and data['daily_breakdown']:
                return pd.DataFrame(data['daily_breakdown'])
            elif 'overall_split' in data and data['overall_split']:
                return pd.DataFrame(data['overall_split'])
            elif 'analysis_period' in data:
                period = data['analysis_period']
                return pd.DataFrame([{
                    'metric': k,
                    'value': v
                } for k, v in period.items()])
        
        elif analysis_id == "los_prediction":
            # Extract ward statistics
            if 'ward_statistics' in data and data['ward_statistics']:
                return pd.DataFrame(data['ward_statistics'])
            elif 'overall_statistics' in data:
                stats = data['overall_statistics']
                return pd.DataFrame([{
                    'metric': k,
                    'value': v
                } for k, v in stats.items()])
        
        elif analysis_id == "staffing":
            # Extract daily forecast or current staff breakdown
            if 'daily_forecast' in data and data['daily_forecast']:
                return pd.DataFrame(data['daily_forecast'])
            elif 'current_staff' in data:
                staff = data['current_staff']
                return pd.DataFrame([{
                    'metric': k,
                    'value': v
                } for k, v in staff.items()])
        
        elif analysis_id == "staff_load":
            # Extract top staff data
            if 'top_staff' in data and data['top_staff']:
                return pd.DataFrame(data['top_staff'])
            elif 'summary_statistics' in data:
                stats = data['summary_statistics']
                return pd.DataFrame([{
                    'metric': k,
                    'value': v
                } for k, v in stats.items()])
        
        return None
    except Exception as e:
        logger.warning(f"Could not force CSV creation for {analysis_id}: {e}")
        return None


def _create_summary_csv(analysis_id: str, data: Dict[str, Any]) -> pd.DataFrame:
    """Create a summary CSV when tabular extraction fails"""
    rows = []
    
    def extract_values(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        # Skip nested objects for summary
                        rows.append({
                            'metric': f"{prefix}{k}_count",
                            'value': len(v),
                            'type': 'count'
                        })
                    else:
                        extract_values(v, f"{prefix}{k}_")
                else:
                    rows.append({
                        'metric': f"{prefix}{k}",
                        'value': v,
                        'type': type(v).__name__
                    })
        elif isinstance(obj, list):
            rows.append({
                'metric': f"{prefix}count",
                'value': len(obj),
                'type': 'count'
            })
    
    extract_values(data)
    
    # Add metadata
    rows.append({
        'metric': 'analysis_id',
        'value': analysis_id,
        'type': 'str'
    })
    rows.append({
        'metric': 'generated_at',
        'value': datetime.now().isoformat(),
        'type': 'timestamp'
    })
    
    return pd.DataFrame(rows)


def save_model_data(analysis_id: str, model_data: Dict[str, Any]) -> str:
    """
    Save model data/parameters to the models folder
    
    Args:
        analysis_id: The analysis identifier
        model_data: Model parameters, configuration, or serialized model
        
    Returns:
        Path to the saved model file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{analysis_id}_model.json"
    filepath = os.path.join(MODEL_DIR, filename)
    
    # Add metadata
    model_with_metadata = {
        "analysis_id": analysis_id,
        "timestamp": timestamp,
        "generated_at": datetime.now().isoformat(),
        "model_data": model_data
    }
    
    with open(filepath, 'w') as f:
        json.dump(model_with_metadata, f, indent=2, default=str)
    
    logger.info(f"Saved model data for {analysis_id} to {filepath}")
    return filepath


def load_analysis_result(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Load the latest analysis result for a given analysis ID
    
    Args:
        analysis_id: The analysis identifier
        
    Returns:
        The loaded result data or None if not found
    """
    json_filepath = os.path.join(RESULT_DIR, f"{analysis_id}_result.json")
    csv_filepath = os.path.join(RESULT_DIR, f"{analysis_id}_result.csv")
    
    # Try JSON first
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON result for {analysis_id}: {e}")
    
    # Try CSV
    if os.path.exists(csv_filepath):
        try:
            df = pd.read_csv(csv_filepath)
            return {
                "analysis_id": analysis_id,
                "timestamp": "unknown",
                "data": df.to_dict('records')
            }
        except Exception as e:
            logger.error(f"Error loading CSV result for {analysis_id}: {e}")
    
    return None


def load_model_data(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Load the latest model data for a given analysis ID
    
    Args:
        analysis_id: The analysis identifier
        
    Returns:
        The loaded model data or None if not found
    """
    filepath = os.path.join(MODEL_DIR, f"{analysis_id}_model.json")
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading model data for {analysis_id}: {e}")
    
    return None


def list_analysis_results() -> Dict[str, Any]:
    """
    List all available analysis results
    
    Returns:
        Dict with analysis IDs and their file info
    """
    results = {}
    
    for filename in os.listdir(RESULT_DIR):
        if filename.endswith('_result.json') or filename.endswith('_result.csv'):
            analysis_id = filename.replace('_result.json', '').replace('_result.csv', '')
            filepath = os.path.join(RESULT_DIR, filename)
            stat = os.stat(filepath)
            
            results[analysis_id] = {
                "filename": filename,
                "filepath": filepath,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "format": "json" if filename.endswith('.json') else "csv"
            }
    
    return results


def list_model_data() -> Dict[str, Any]:
    """
    List all available model data files
    
    Returns:
        Dict with analysis IDs and their model file info
    """
    models = {}
    
    for filename in os.listdir(MODEL_DIR):
        if filename.endswith('_model.json'):
            analysis_id = filename.replace('_model.json', '')
            filepath = os.path.join(MODEL_DIR, filename)
            stat = os.stat(filepath)
            
            models[analysis_id] = {
                "filename": filename,
                "filepath": filepath,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
    
    return models 