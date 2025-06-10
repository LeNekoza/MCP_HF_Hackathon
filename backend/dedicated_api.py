"""
Dedicated API endpoints for each analysis with result storage
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# For FastAPI integration (optional)
try:
    from fastapi import FastAPI, HTTPException, Request, Query
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .analytics import occupancy, census_forecast, admission_split, los_model, burn_rate, staffing, average_los, tool_utilisation, inventory_expiry, staff_load
from .storage import (
    save_analysis_result, 
    save_model_data, 
    load_analysis_result, 
    load_model_data,
    list_analysis_results,
    list_model_data
)

logger = logging.getLogger(__name__)


def create_dedicated_analytics_api() -> Any:
    """
    Create FastAPI application with dedicated endpoints for each analysis
    
    Returns:
        FastAPI app instance or None if FastAPI not available
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI not available. Cannot create API endpoints.")
        return None
    
    app = FastAPI(
        title="Smart Hospital Analytics - Dedicated API",
        description="Dedicated endpoints for hospital analytics with automatic result storage",
        version="2.0.0"
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "Smart Hospital Analytics - Dedicated API",
            "version": "2.0.0",
            "features": [
                "Dedicated endpoints for each analysis",
                "Automatic result storage",
                "Model parameter persistence",
                "Historical result access"
            ],
            "analysis_endpoints": [
                "/bed-snapshot",
                "/census-forecast",
                "/admission-split", 
                "/los-prediction",
                "/burn-rate",
                "/staffing",
                "/average-los",
                "/tool-utilisation",
                "/inventory-expiry",
                "/staff-load"
            ],
            "utility_endpoints": [
                "/results",
                "/models",
                "/results/{analysis_id}",
                "/models/{analysis_id}"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "dedicated_analytics_api",
            "storage_directories": ["result", "models"]
        }
    
    # Dedicated analysis endpoints
    
    @app.post("/bed-snapshot")
    @app.get("/bed-snapshot")
    async def get_bed_snapshot(
        date: Optional[str] = Query(None, description="Snapshot date (YYYY-MM-DD format)")
    ):
        """Get real-time bed occupancy snapshot - recomputes and saves results"""
        try:
            # Parse date if provided
            snapshot_date = None
            if date:
                snapshot_date = datetime.fromisoformat(date)
            
            # Recompute analysis and save results
            result = occupancy.get_bed_snapshot(date=snapshot_date, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "bed_snapshot",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in bed-snapshot endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/census-forecast")
    @app.get("/census-forecast")
    async def get_census_forecast(
        days: int = Query(3, ge=1, le=7, description="Number of days to forecast")
    ):
        """Get bed census forecast - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = census_forecast.forecast_bed_census(days=days, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "census_forecast",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in census-forecast endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/admission-split")
    @app.get("/admission-split")
    async def get_admission_split(
        days_back: int = Query(14, ge=1, le=90, description="Number of days to analyze back")
    ):
        """Get admission split analysis - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = admission_split.admission_split(days_back=days_back, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "admission_split",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in admission-split endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/los-prediction")
    @app.get("/los-prediction")
    async def get_los_prediction():
        """Get length of stay prediction analysis - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = los_model.los_summary(save_results=True)
            
            return {
                "success": True,
                "analysis_id": "los_prediction",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in los-prediction endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/burn-rate")
    @app.get("/burn-rate") 
    async def get_burn_rate(
        days: int = Query(7, ge=1, le=30, description="Number of days to forecast")
    ):
        """Get consumable burn rate forecast - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = burn_rate.forecast_consumables(days=days, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "burn_rate",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in burn-rate endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/staffing")
    @app.get("/staffing")
    async def get_staffing(
        days: int = Query(3, ge=1, le=7, description="Number of days to forecast")
    ):
        """Get staffing requirements forecast - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = staffing.forecast_staff(days=days, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "staffing",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in staffing endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/average-los")
    @app.get("/average-los")
    async def get_average_los():
        """Get average length of stay by ward - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = average_los.average_los_by_ward(save_results=True)
            
            return {
                "success": True,
                "analysis_id": "average_los",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in average-los endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tool-utilisation")
    @app.get("/tool-utilisation")
    async def get_tool_utilisation(
        top_n: int = Query(10, ge=5, le=50, description="Number of top tools to return")
    ):
        """Get tool utilisation analysis - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = tool_utilisation.tool_utilisation_analysis(top_n=top_n, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "tool_utilisation",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in tool-utilisation endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/inventory-expiry")
    @app.get("/inventory-expiry")
    async def get_inventory_expiry(
        days_threshold: int = Query(90, ge=7, le=365, description="Days ahead to check for expiry")
    ):
        """Get inventory expiry analysis - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = inventory_expiry.inventory_expiry_analysis(days_threshold=days_threshold, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "inventory_expiry",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in inventory-expiry endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/staff-load")
    @app.get("/staff-load")
    async def get_staff_load(
        top_n: int = Query(10, ge=5, le=50, description="Number of top staff to return")
    ):
        """Get staff workload analysis - recomputes and saves results"""
        try:
            # Recompute analysis and save results
            result = staff_load.staff_load_analysis(top_n=top_n, save_results=True)
            
            return {
                "success": True,
                "analysis_id": "staff_load",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error in staff-load endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Model training endpoints
    
    @app.post("/los-prediction/train")
    async def train_los_model():
        """Train the Length of Stay prediction model"""
        try:
            predictor = los_model.LOSPredictor()
            result = predictor.train()
            
            return {
                "success": True,
                "analysis_id": "los_prediction_training",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "stored": True
            }
            
        except Exception as e:
            logger.error(f"Error training LOS model: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Utility endpoints for accessing stored results and models
    
    @app.get("/results")
    async def list_all_results():
        """List all stored analysis results"""
        try:
            results = list_analysis_results()
            return {
                "success": True,
                "data": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error listing results: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/models")
    async def list_all_models():
        """List all stored model data"""
        try:
            models = list_model_data()
            return {
                "success": True,
                "data": models,
                "count": len(models)
            }
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/results/{analysis_id}")
    async def get_stored_result(analysis_id: str):
        """Get stored result for a specific analysis"""
        try:
            result = load_analysis_result(analysis_id)
            if result is None:
                raise HTTPException(status_code=404, detail=f"No stored result found for {analysis_id}")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "data": result
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error loading result for {analysis_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/models/{analysis_id}")
    async def get_stored_model(analysis_id: str):
        """Get stored model data for a specific analysis"""
        try:
            model_data = load_model_data(analysis_id)
            if model_data is None:
                raise HTTPException(status_code=404, detail=f"No stored model found for {analysis_id}")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "data": model_data
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error loading model for {analysis_id}: {str(e)}")
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