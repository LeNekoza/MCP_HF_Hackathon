#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced analytics UI components.
This creates a standalone Gradio interface with just the analytics dashboard.
"""

import gradio as gr
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.components.analytics_interface import create_analytics_dashboard

def main():
    """Create and launch the analytics dashboard test interface."""
    
    with gr.Blocks(
        title="Hospital Analytics Dashboard - UI Test",
        css="""
        .analytics-dashboard {
            padding: 20px;
            background: white;
            border-radius: 12px;
            margin: 0;
        }

        .analytics-header {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
        }

        .analytics-header h2 {
            color: #1f2937;
            margin: 0 0 5px 0;
            font-size: 24px;
            font-weight: 600;
        }

        .analytics-header p {
            color: #6b7280;
            margin: 0;
            font-size: 14px;
        }

        .analytics-controls {
            margin-bottom: 20px;
        }

        .analysis-selector, .chart-type-selector {
            margin-bottom: 15px;
        }

        .refresh-btn {
            height: 40px;
            font-weight: 500;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }

        .refresh-btn:hover {
            background: #2563eb;
        }

        .analysis-description {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }

        .analysis-description p {
            margin: 0 0 5px 0;
            color: #374151;
        }

        .analysis-description small {
            color: #6b7280;
            font-size: 12px;
        }

        .main-chart {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 20px;
            background: white;
        }

        .summary-panel {
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e5e7eb;
            height: fit-content;
        }

        .summary-panel h3 {
            margin: 0 0 15px 0;
            color: #1f2937;
            font-size: 18px;
            font-weight: 600;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }

        .metric:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #6b7280;
            font-size: 14px;
        }

        .metric-value {
            color: #1f2937;
            font-weight: 600;
            font-size: 16px;
        }
        """,
        fill_height=True
    ) as demo:
        
        gr.HTML("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-bottom: 20px;">
                <h1>🏥 Hospital Analytics Dashboard - UI Test</h1>
                <p>Demonstrating the enhanced analytics interface with dynamic dropdowns, refresh functionality, and interactive charts</p>
            </div>
        """)
        
        # Create the analytics dashboard
        analytics_dashboard, analysis_selector, chart_type_selector, chart_display, summary_display = create_analytics_dashboard()
        
        gr.HTML("""
            <div style="padding: 20px; background: #f8fafc; border-radius: 8px; margin-top: 20px;">
                <h3>✅ UI Features Implemented:</h3>
                <ul>
                    <li><strong>📊 Analysis Dropdown:</strong> Dynamic list of available analyses from registry</li>
                    <li><strong>📈 Chart Type Selector:</strong> Updates dynamically based on selected analysis</li>
                    <li><strong>🔄 Refresh Button:</strong> Positioned next to analysis selector for data refresh</li>
                    <li><strong>📊 Interactive Graph:</strong> Reuses existing gr.Plot component with dynamic data</li>
                    <li><strong>📋 Summary Panel:</strong> Shows analysis-specific metrics and statistics</li>
                    <li><strong>⚡ Async Data Fetching:</strong> Backend integration with graceful fallback to mock data</li>
                </ul>
                <p><em>The interface automatically loads bed occupancy data on startup and allows switching between different analysis types.</em></p>
            </div>
        """)
    
    print("🚀 Starting Hospital Analytics Dashboard UI Test...")
    print("📊 Features: Dynamic analysis selector, chart type controls, refresh functionality")
    print("🔗 Open http://localhost:7860 to view the enhanced analytics interface")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        debug=True
    )

if __name__ == "__main__":
    main() 