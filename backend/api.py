"""
API endpoints for Smart Hospital Analytics Backend
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# For FastAPI integration (optional)
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .analysis_registry import (
    get_analysis, 
    get_analysis_metadata, 
    get_analysis_list, 
    get_chart_options,
    execute_analysis
)

logger = logging.getLogger(__name__)

# Pydantic models for request validation (if FastAPI is available)
if FASTAPI_AVAILABLE:
    class AnalysisRequest(BaseModel):
        analysis_id: str
        parameters: Optional[Dict[str, Any]] = None

    class ChartRequest(BaseModel):
        analysis_id: str


def create_analytics_api() -> Any:
    """
    Create FastAPI application for analytics endpoints
    
    Returns:
        FastAPI app instance or None if FastAPI not available
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI not available. Cannot create API endpoints.")
        return None
    
    app = FastAPI(
        title="Smart Hospital Analytics API",
        description="Backend API for hospital analytics and insights",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "Smart Hospital Analytics API",
            "version": "1.0.0",
            "available_endpoints": [
                "/analyses",
                "/analyses/metadata", 
                "/analyses/{analysis_id}",
                "/analyses/{analysis_id}/charts",
                "/health"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "analytics_backend"
        }
    
    @app.get("/analyses")
    async def list_analyses():
        """Get list of available analyses"""
        try:
            return {
                "success": True,
                "data": get_analysis_list()
            }
        except Exception as e:
            logger.error(f"Error listing analyses: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/analyses/metadata")
    async def get_analyses_metadata():
        """Get metadata for all analyses"""
        try:
            return {
                "success": True,
                "data": get_analysis_metadata()
            }
        except Exception as e:
            logger.error(f"Error getting metadata: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/analyses/{analysis_id}")
    async def get_analysis_data(analysis_id: str, request: Request):
        """Get data for a specific analysis with optional parameters"""
        try:
            # Extract query parameters
            parameters = dict(request.query_params)
            
            # Convert numeric parameters
            for key, value in parameters.items():
                if value.isdigit():
                    parameters[key] = int(value)
                elif value.lower() in ['true', 'false']:
                    parameters[key] = value.lower() == 'true'
            
            result = execute_analysis(analysis_id, parameters)
            
            if not result.get("success", False):
                raise HTTPException(
                    status_code=400, 
                    detail=result.get("error", "Analysis execution failed")
                )
            
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error executing analysis {analysis_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/analyses/execute")
    async def execute_analysis_post(request: AnalysisRequest):
        """Execute analysis via POST with parameters in body"""
        try:
            result = execute_analysis(
                request.analysis_id, 
                request.parameters or {}
            )
            
            if not result.get("success", False):
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error", "Analysis execution failed")
                )
            
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error executing analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/analyses/{analysis_id}/charts")
    async def get_chart_options_endpoint(analysis_id: str):
        """Get available chart types for an analysis"""
        try:
            return {
                "success": True,
                "data": get_chart_options(analysis_id)
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting chart options: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": str(exc) if logger.level <= logging.DEBUG else "An error occurred"
            }
        )
    
    return app


# Simple function-based API for Gradio integration
def get_analysis_for_gradio(analysis_id: str, **kwargs) -> Dict[str, Any]:
    """
    Gradio-compatible function for getting analysis data
    
    Args:
        analysis_id: The analysis to execute
        **kwargs: Parameters for the analysis
        
    Returns:
        Analysis result formatted for Gradio
    """
    try:
        result = execute_analysis(analysis_id, kwargs)
        
        if result.get("success", False):
            return {
                "success": True,
                "analysis_id": analysis_id,
                "label": result["analysis_metadata"]["label"],
                "default_chart": result["analysis_metadata"]["default_chart"],
                "extra_charts": result["analysis_metadata"]["extra_charts"],
                "data": result["data"],
                "timestamp": result["timestamp"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "analysis_id": analysis_id
            }
            
    except Exception as e:
        logger.error(f"Error in Gradio API: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "analysis_id": analysis_id
        }


def get_analyses_list_for_gradio() -> list:
    """
    Get analyses list formatted for Gradio dropdown
    
    Returns:
        List of (label, value) tuples for Gradio
    """
    try:
        analyses = get_analysis_list()
        return [(item["label"], item["id"]) for item in analyses]
    except Exception as e:
        logger.error(f"Error getting analyses list: {str(e)}")
        return [("Error loading analyses", "error")]


# Convenience function for testing
def test_analysis(analysis_id: str = "bed_snapshot") -> Dict[str, Any]:
    """
    Test function to verify backend is working
    
    Args:
        analysis_id: Analysis to test (defaults to bed_snapshot)
        
    Returns:
        Test result
    """
    try:
        result = execute_analysis(analysis_id)
        return {
            "test_status": "success",
            "analysis_tested": analysis_id,
            "data_available": bool(result.get("data")),
            "success": result.get("success", False)
        }
    except Exception as e:
        return {
            "test_status": "error",
            "analysis_tested": analysis_id,
            "error": str(e),
            "success": False
        } 