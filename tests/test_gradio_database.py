#!/usr/bin/env python3
"""
Test script for Gradio Database Interface Integration
Tests the database tab functionality
"""

import sys
import os
sys.path.append('src')

import gradio as gr
from src.components.database_interface import create_database_tab

def create_test_interface():
    """Create a simple test interface with the database tab"""
    
    with gr.Blocks(title="Database Integration Test") as demo:
        gr.Markdown("# Database Integration Test")
        
        with gr.Tabs():
            # Add the database tab
            database_tab = create_database_tab()
            
            # Add a simple test tab
            with gr.TabItem("Test Info"):
                gr.Markdown("""
                ## NeonDB PostgreSQL Integration Test
                
                This interface tests the database integration with your hospital data.
                
                ### Features:
                - ✅ Database connection status
                - ✅ Patient search functionality
                - ✅ Room availability checking
                - ✅ Medical equipment inventory
                - ✅ Staff directory
                - ✅ Real-time database statistics
                
                ### Data Available:
                - **3,210** Users (patients, staff, admins)
                - **3,000** Patient Records
                - **150** Hospital Rooms
                - **500** Medical Tools/Equipment
                - **100** Inventory Items
                - **50** Storage Rooms
                - **1,100** Occupancy Records
                
                Switch to the "Hospital Database" tab to explore the data!
                """)
    
    return demo

if __name__ == "__main__":
    print("🏥 Starting Database Integration Test...")
    print("This will launch a Gradio interface to test the database functionality.")
    
    # Create and launch the test interface
    demo = create_test_interface()
    
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7861,  # Different port to avoid conflicts
            share=False,
            debug=True,
            show_api=False
        )
    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        sys.exit(1) 