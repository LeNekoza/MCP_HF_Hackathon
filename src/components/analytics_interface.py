"""
Analytics Interface Component for Smart Hospital Dashboard.
"""
import gradio as gr
import json
import asyncio
import requests
import os
from typing import Dict, Any, Tuple, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Analysis registry - matches backend/analysis_registry.py
ANALYSES = {
    "bed_snapshot": {
        "label": "Real-time bed occupancy by ward",
        "default_chart": "stacked_bar",
        "extra_charts": ["bar", "pie"],
        "category": "occupancy"
    },
    "census_forecast": {
        "label": "Short-horizon bed census forecast",
        "default_chart": "line",
        "extra_charts": ["line_conf_band", "scatter"],
        "category": "forecasting"
    },
    "admission_split": {
        "label": "Elective vs emergency demand split",
        "default_chart": "stacked_bar",
        "extra_charts": ["pie", "bar"],
        "category": "demand"
    },
    "los_prediction": {
        "label": "Average length-of-stay analysis",
        "default_chart": "bar",
        "extra_charts": ["box", "scatter"],
        "category": "prediction"
    },
    "burn_rate": {
        "label": "Consumable burn-rate forecast",
        "default_chart": "stacked_area",
        "extra_charts": ["line", "bar"],
        "category": "inventory"
    },
    "staffing": {
        "label": "Staffing needs forecast",
        "default_chart": "grouped_bar",
        "extra_charts": ["dual_axis_line", "line"],
        "category": "workforce"
    }
}

def get_backend_url():
    """Get the backend URL for API calls."""
    return os.getenv("BACKEND_URL", "http://localhost:8000")

async def fetch_analysis_data(analysis_id: str) -> Dict[str, Any]:
    """Fetch analysis data from backend API."""
    try:
        backend_url = get_backend_url()
        response = requests.post(
            f"{backend_url}/get_analysis",
            json={"analysis_id": analysis_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback to mock data if backend unavailable
            return generate_mock_data(analysis_id)
    except Exception as e:
        print(f"Error fetching analysis data: {e}")
        return generate_mock_data(analysis_id)

def generate_mock_data(analysis_id: str) -> Dict[str, Any]:
    """Generate mock data for testing when backend is unavailable."""
    import random
    import datetime as dt
    
    if analysis_id == "bed_snapshot":
        return {
            "data": {
                "wards": ["ICU", "Emergency", "General", "Cardiac", "Pediatric"],
                "occupied": [8, 12, 25, 6, 10],
                "capacity": [10, 15, 30, 8, 12],
                "utilization": [80, 80, 83, 75, 83]
            },
            "default_chart": "stacked_bar",
            "extra_charts": ["bar", "pie"]
        }
    elif analysis_id == "admission_split":
        return {
            "data": {
                "categories": ["Elective", "Emergency"],
                "counts": [48, 52],
                "weekly_trend": [
                    {"date": "2024-01-01", "elective": 45, "emergency": 55},
                    {"date": "2024-01-08", "elective": 48, "emergency": 52},
                    {"date": "2024-01-15", "elective": 50, "emergency": 50}
                ]
            },
            "default_chart": "stacked_bar",
            "extra_charts": ["pie", "bar"]
        }
    else:
        # Generic mock data
        return {
            "data": {
                "x": [f"Item {i}" for i in range(1, 6)],
                "y": [random.randint(10, 100) for _ in range(5)]
            },
            "default_chart": ANALYSES[analysis_id]["default_chart"],
            "extra_charts": ANALYSES[analysis_id]["extra_charts"]
        }

def create_plotly_chart(data: Dict[str, Any], chart_type: str, analysis_id: str):
    """Create Plotly chart based on data and chart type."""
    try:
        if analysis_id == "bed_snapshot" and "wards" in data:
            if chart_type == "stacked_bar":
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Occupied',
                    x=data["wards"],
                    y=data["occupied"],
                    marker_color='#ef4444'
                ))
                fig.add_trace(go.Bar(
                    name='Available',
                    x=data["wards"],
                    y=[data["capacity"][i] - data["occupied"][i] for i in range(len(data["wards"]))],
                    marker_color='#22c55e'
                ))
                fig.update_layout(
                    title="Bed Occupancy by Ward",
                    barmode='stack',
                    xaxis_title="Ward",
                    yaxis_title="Number of Beds"
                )
                return fig
            elif chart_type == "pie":
                total_occupied = sum(data["occupied"])
                total_available = sum(data["capacity"]) - total_occupied
                fig = go.Figure(data=[go.Pie(
                    labels=['Occupied', 'Available'],
                    values=[total_occupied, total_available],
                    marker_colors=['#ef4444', '#22c55e']
                )])
                fig.update_layout(title="Overall Bed Utilization")
                return fig
                
        elif analysis_id == "admission_split" and "categories" in data:
            if chart_type == "pie":
                fig = go.Figure(data=[go.Pie(
                    labels=data["categories"],
                    values=data["counts"],
                    marker_colors=['#3b82f6', '#f59e0b']
                )])
                fig.update_layout(title="Admission Type Distribution")
                return fig
            elif chart_type == "stacked_bar":
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Elective',
                    x=data["categories"],
                    y=[data["counts"][0] if i == 0 else 0 for i in range(len(data["categories"]))],
                    marker_color='#3b82f6'
                ))
                fig.add_trace(go.Bar(
                    name='Emergency',
                    x=data["categories"],
                    y=[0 if i == 0 else data["counts"][1] for i in range(len(data["categories"]))],
                    marker_color='#f59e0b'
                ))
                fig.update_layout(
                    title="Admission Types",
                    barmode='group',
                    xaxis_title="Category",
                    yaxis_title="Count"
                )
                return fig
        
        # Generic fallback chart
        if "x" in data and "y" in data:
            if chart_type == "line":
                fig = go.Figure(data=go.Scatter(x=data["x"], y=data["y"], mode='lines+markers'))
            elif chart_type == "bar":
                fig = go.Figure(data=go.Bar(x=data["x"], y=data["y"]))
            else:
                fig = go.Figure(data=go.Scatter(x=data["x"], y=data["y"], mode='markers'))
            
            fig.update_layout(title=f"Analysis: {ANALYSES[analysis_id]['label']}")
            return fig
            
    except Exception as e:
        print(f"Error creating chart: {e}")
        # Return empty figure on error
        fig = go.Figure()
        fig.add_annotation(
            text="Error loading chart data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle'
        )
        return fig
    
    # Default empty chart
    return go.Figure()

def get_analysis_summary(data: Dict[str, Any], analysis_id: str) -> str:
    """Generate summary HTML for analysis data."""
    try:
        if analysis_id == "bed_snapshot" and "wards" in data:
            total_occupied = sum(data["occupied"])
            total_capacity = sum(data["capacity"])
            utilization = round((total_occupied / total_capacity) * 100, 1)
            
            return f"""
            <div class="summary-panel">
                <h3>📊 Bed Occupancy Summary</h3>
                <div class="metric">
                    <span class="metric-label">Total Beds:</span>
                    <span class="metric-value">{total_capacity}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Occupied:</span>
                    <span class="metric-value">{total_occupied}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Utilization:</span>
                    <span class="metric-value">{utilization}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Available:</span>
                    <span class="metric-value">{total_capacity - total_occupied}</span>
                </div>
            </div>
            """
        elif analysis_id == "admission_split" and "categories" in data:
            total = sum(data["counts"])
            elective_pct = round((data["counts"][0] / total) * 100, 1)
            emergency_pct = round((data["counts"][1] / total) * 100, 1)
            
            return f"""
            <div class="summary-panel">
                <h3>🚑 Admission Summary</h3>
                <div class="metric">
                    <span class="metric-label">Total Admissions:</span>
                    <span class="metric-value">{total}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Elective:</span>
                    <span class="metric-value">{elective_pct}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Emergency:</span>
                    <span class="metric-value">{emergency_pct}%</span>
                </div>
            </div>
            """
        else:
            return f"""
            <div class="summary-panel">
                <h3>📈 Analysis Summary</h3>
                <p>{ANALYSES[analysis_id]['label']}</p>
                <p>Data loaded successfully</p>
            </div>
            """
    except Exception as e:
        return f"""
        <div class="summary-panel">
            <h3>⚠️ Summary</h3>
            <p>Error generating summary: {str(e)}</p>
        </div>
        """

def create_analytics_dashboard():
    """Create the analytics dashboard component."""
    
    # Analysis choices from registry
    analysis_choices = [(info["label"], analysis_id) for analysis_id, info in ANALYSES.items()]
    
    # State management
    current_data = gr.State({})
    
    with gr.Column(elem_classes="analytics-dashboard") as dashboard:
        
   
        
        # Controls Section - Analysis selector and Refresh button on same row
        with gr.Row(elem_classes="analytics-controls"):
            with gr.Column(scale=3):
                analysis_selector = gr.Dropdown(
                    choices=analysis_choices,
                    value="bed_snapshot",
                    label="📊 Select Analysis",
                    info="Choose the type of analysis to run",
                    elem_classes="analysis-selector"
                )
            
            with gr.Column(scale=1):
                refresh_btn = gr.Button(
                    "🔄 Refresh",
                    variant="primary",
                    elem_classes="refresh-btn"
                )
        
        # Chart Type Selector (dynamic)
        chart_type_selector = gr.Dropdown(
            choices=["stacked_bar"],  # Will be updated dynamically
            value="stacked_bar",
            label="📈 Chart Type",
            info="Visualization style",
            elem_classes="chart-type-selector"
        )
        
        # Status and Description
      
        
        # Main Content Area
        with gr.Row():
            # Chart Display - Using existing interactive graph component
            with gr.Column(scale=3):
                chart_display = gr.Plot(
                    label="📊 Visualization",
                    elem_classes="main-chart"
                )
            
            # Data Summary
            with gr.Column(scale=1):
                summary_display = gr.HTML(
                    """<div class="summary-panel">
                        <h3>Summary</h3>
                        <p>Select an analysis to view summary statistics</p>
                    </div>""",
                    elem_classes="summary-panel"
                )
        
        # Event handlers
        async def update_analysis(analysis_id: str):
            """Update analysis data and chart options."""
            try:
                # Get analysis info
                analysis_info = ANALYSES[analysis_id]
                
                # Build chart choices - default + extra
                chart_choices = [analysis_info["default_chart"]] + analysis_info["extra_charts"]
                default_chart = analysis_info["default_chart"]
                
                # Update description
                description_html = f"""
                <div class="analysis-description">
                    <p><strong>{analysis_info['label']}:</strong> Loading analysis data...</p>
                </div>
                """
                
                # Fetch data from backend (with caching logic would go here)
                data_response = await fetch_analysis_data(analysis_id)
                
                # Create initial chart
                chart_fig = create_plotly_chart(data_response["data"], default_chart, analysis_id)
                
                # Generate summary
                summary_html = get_analysis_summary(data_response["data"], analysis_id)
                
                # Update description with success
                description_html = f"""
                <div class="analysis-description">
                    <p><strong>{analysis_info['label']}:</strong> Analysis completed successfully</p>
                    <small>Category: {analysis_info['category'].title()} | Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')}</small>
                </div>
                """
                
                return (
                    gr.Dropdown(choices=chart_choices, value=default_chart),  # chart_type_selector
                    chart_fig,  # chart_display
                    summary_html,  # summary_display  
      
                    data_response  # current_data
                )
                
            except Exception as e:
                error_msg = f"Error loading analysis: {str(e)}"
                return (
                    gr.Dropdown(choices=["error"], value="error"),
                    go.Figure().add_annotation(text=error_msg, x=0.5, y=0.5),
                    f"<div class='summary-panel'><h3>Error</h3><p>{error_msg}</p></div>",
                    f"<div class='analysis-description'><p>Error: {error_msg}</p></div>",
                    {}
                )
        
        def update_chart_type(analysis_id: str, chart_type: str, data: Dict):
            """Update chart when chart type changes."""
            try:
                if not data or "data" not in data:
                    return go.Figure().add_annotation(text="No data available", x=0.5, y=0.5)
                
                return create_plotly_chart(data["data"], chart_type, analysis_id)
            except Exception as e:
                return go.Figure().add_annotation(text=f"Chart error: {str(e)}", x=0.5, y=0.5)
        
        # Wire up event handlers
        analysis_selector.change(
            fn=update_analysis,
            inputs=[analysis_selector],
            outputs=[chart_type_selector, chart_display, summary_display,  current_data]
        )
        
        chart_type_selector.change(
            fn=update_chart_type,
            inputs=[analysis_selector, chart_type_selector, current_data],
            outputs=[chart_display]
        )
        
        refresh_btn.click(
            fn=update_analysis,
            inputs=[analysis_selector],
            outputs=[chart_type_selector, chart_display, summary_display, current_data]
        )
        
        # Event handlers are now set up - initialization will be handled by parent component
    
    return dashboard, analysis_selector, chart_type_selector, chart_display, summary_display 