"""
API endpoints for Smart Hospital Analytics.
Provides REST endpoints for all analytics functions.
"""
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio

from .analysis_registry import ANALYSES, run_analysis, get_analysis_list, get_analysis_by_category


app = FastAPI(title="Smart Hospital Analytics API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    analysis_id: str
    parameters: Optional[Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Smart Hospital Analytics API", "status": "healthy"}


@app.get("/analyses")
async def list_analyses():
    """Get list of all available analyses."""
    return {
        "analyses": get_analysis_list(),
        "categories": get_analysis_by_category()
    }


@app.post("/get_analysis")
async def get_analysis(request: AnalysisRequest):
    """
    Run a specific analysis and return results.
    
    Args:
        request: Analysis request with ID and parameters
        
    Returns:
        Analysis results with metadata
    """
    try:
        result = await run_analysis(
            request.analysis_id, 
            **request.parameters
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{analysis_id}")
async def get_analysis_by_id(analysis_id: str):
    """
    Run a specific analysis by ID (GET method for simple cases).
    
    Args:
        analysis_id: The ID of the analysis to run
        
    Returns:
        Analysis results with metadata
    """
    try:
        result = await run_analysis(analysis_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{analysis_id}/metadata")
async def get_analysis_metadata(analysis_id: str):
    """Get metadata for a specific analysis without running it."""
    if analysis_id not in ANALYSES:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    config = ANALYSES[analysis_id]
    return {
        "analysis_id": analysis_id,
        "label": config["label"],
        "description": config["description"],
        "category": config["category"],
        "default_chart": config["default_chart"],
        "extra_charts": config["extra_charts"]
    }


# Gradio integration functions
def create_gradio_analytics_interface():
    """Create Gradio interface components for analytics."""
    import gradio as gr
    
    # Analysis selector dropdown
    analysis_choices = [(config["label"], analysis_id) 
                       for analysis_id, config in ANALYSES.items()]
    
    with gr.Column() as analytics_interface:
        with gr.Row():
            analysis_selector = gr.Dropdown(
                choices=analysis_choices,
                value="bed_snapshot",
                label="Select Analysis",
                elem_classes="analysis-selector"
            )
            refresh_btn = gr.Button(
                "🔄 Refresh Data",
                elem_classes="refresh-btn",
                size="sm"
            )
        
        # Chart type selector (will be updated dynamically)
        chart_type_selector = gr.Dropdown(
            choices=["line", "bar", "scatter", "pie"],
            value="bar",
            label="Chart Type",
            elem_classes="chart-type-selector"
        )
        
        # Results display
        analysis_output = gr.JSON(
            label="Analysis Results",
            elem_classes="analysis-results"
        )
        
        # Chart display (placeholder for now)
        chart_display = gr.Plot(
            label="Chart Visualization",
            elem_classes="chart-display"
        )
        
        async def run_selected_analysis(analysis_id, chart_type):
            """Run the selected analysis and return results."""
            try:
                result = await run_analysis(analysis_id)
                
                # Update chart type options based on analysis
                if "data" in result and not result.get("error"):
                    config = ANALYSES[analysis_id]
                    available_charts = [config["default_chart"]] + config["extra_charts"]
                    
                    return (
                        result,
                        gr.Dropdown(choices=available_charts, value=config["default_chart"]),
                        result["data"]  # For chart display
                    )
                else:
                    return result, chart_type_selector, None
                    
            except Exception as e:
                return {"error": str(e)}, chart_type_selector, None
        
        # Event handlers
        analysis_selector.change(
            run_selected_analysis,
            inputs=[analysis_selector, chart_type_selector],
            outputs=[analysis_output, chart_type_selector, chart_display]
        )
        
        refresh_btn.click(
            run_selected_analysis,
            inputs=[analysis_selector, chart_type_selector],
            outputs=[analysis_output, chart_type_selector, chart_display]
        )
    
    return analytics_interface, analysis_selector, chart_type_selector, analysis_output


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8001)),
        log_level="info"
    ) 