"""
Database Interface Components for NeonDB Integration
Provides Gradio components for hospital data visualization and queries
"""

import gradio as gr
import pandas as pd
from typing import Dict, Any, Tuple, List
import logging

from ..utils.database import get_data_retriever, test_database_connection
from ..utils.logger import setup_logger

logger = setup_logger()


def create_database_tab() -> gr.TabItem:
    """
    Create a database tab for hospital data exploration
    
    Returns:
        gr.TabItem: Database interface tab
    """
    with gr.TabItem("🏥 Hospital Database", elem_id="database-tab") as tab:
        
        # Header
        gr.Markdown("""
        # Hospital Database Dashboard
        Explore and query hospital data from NeonDB PostgreSQL
        """)
        
        # Database connection status
        with gr.Row():
            connection_status = gr.Textbox(
                label="Database Status",
                value="Testing connection...",
                interactive=False,
                elem_classes="status-box"
            )
            refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")
        
        # Database overview section
        with gr.Accordion("📊 Database Overview", open=True):
            overview_display = gr.Markdown("Loading database statistics...")
        
        # Patient search section
        with gr.Accordion("🔍 Patient Search", open=False):
            with gr.Row():
                search_input = gr.Textbox(
                    label="Search patients by name",
                    placeholder="Enter patient name...",
                    scale=3
                )
                search_btn = gr.Button("Search", variant="primary", scale=1)
            
            patient_results = gr.Dataframe(
                headers=["ID", "Name", "DOB", "Blood Type", "Phone"],
                interactive=False,
                wrap=True
            )
        
        # Room availability section
        with gr.Accordion("🏠 Room Availability", open=False):
            with gr.Row():
                room_type_filter = gr.Dropdown(
                    label="Room Type",
                    choices=["All", "Emergency", "Surgery", "General Ward", "ICU", "Pediatric"],
                    value="All",
                    scale=2
                )
                available_only_check = gr.Checkbox(
                    label="Available rooms only",
                    value=True,
                    scale=1
                )
                get_rooms_btn = gr.Button("Get Rooms", variant="primary", scale=1)
            
            room_results = gr.Dataframe(
                headers=["Room Number", "Type", "Floor", "Beds", "Available"],
                interactive=False,
                wrap=True
            )
        
        # Medical equipment section
        with gr.Accordion("🩺 Medical Equipment", open=False):
            with gr.Row():
                equipment_available_only = gr.Checkbox(
                    label="Available equipment only",
                    value=True,
                    scale=2
                )
                get_equipment_btn = gr.Button("Get Equipment", variant="primary", scale=1)
            
            equipment_results = gr.Dataframe(
                headers=["Equipment", "Category", "Available Qty", "Total Qty", "Location"],
                interactive=False,
                wrap=True
            )
        
        # Staff overview section
        with gr.Accordion("👨‍⚕️ Medical Staff", open=False):
            with gr.Row():
                staff_type_filter = gr.Dropdown(
                    label="Staff Type",
                    choices=["All", "doctor", "nurse", "admin", "technician"],
                    value="All",
                    scale=2
                )
                get_staff_btn = gr.Button("Get Staff", variant="primary", scale=1)
            
            staff_results = gr.Dataframe(
                headers=["Name", "Role", "Staff Type", "Email"],
                interactive=False,
                wrap=True
            )
        
        # Event handlers
        def check_database_connection():
            """Check database connection status"""
            try:
                if test_database_connection():
                    return "✅ Connected to NeonDB PostgreSQL", get_database_overview()
                else:
                    return "❌ Database connection failed", "Could not connect to database"
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                return f"❌ Error: {str(e)}", "Database connection error"
        
        def get_database_overview():
            """Get database statistics overview"""
            try:
                retriever = get_data_retriever()
                stats = retriever.get_database_stats()
                
                overview = "## 📈 Database Statistics\n\n"
                total_records = sum(stats.values())
                overview += f"**Total Records:** {total_records:,}\n\n"
                
                for table, count in stats.items():
                    table_name = table.replace('_', ' ').title()
                    overview += f"• **{table_name}:** {count:,} records\n"
                
                overview += "\n---\n"
                overview += "*Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "*"
                
                return overview
            except Exception as e:
                logger.error(f"Error getting database overview: {e}")
                return f"❌ Error loading database overview: {str(e)}"
        
        def search_patients(search_term: str):
            """Search for patients by name"""
            if not search_term.strip():
                return pd.DataFrame()
            
            try:
                retriever = get_data_retriever()
                patients_df = retriever.search_patients_by_name(search_term)
                
                if patients_df.empty:
                    return pd.DataFrame(columns=["ID", "Name", "DOB", "Blood Type", "Phone"])
                
                # Format the data for display
                display_df = patients_df[['id', 'full_name', 'date_of_birth', 'blood_group', 'phone_number']].copy()
                display_df.columns = ["ID", "Name", "DOB", "Blood Type", "Phone"]
                
                # Convert phone_number JSON to string
                if 'Phone' in display_df.columns:
                    display_df['Phone'] = display_df['Phone'].apply(
                        lambda x: x.get('primary', 'N/A') if isinstance(x, dict) else str(x)
                    )
                
                return display_df.head(20)  # Limit to 20 results
            except Exception as e:
                logger.error(f"Error searching patients: {e}")
                return pd.DataFrame(columns=["ID", "Name", "DOB", "Blood Type", "Phone"])
        
        def get_rooms(room_type: str, available_only: bool):
            """Get room information"""
            try:
                retriever = get_data_retriever()
                
                # Filter by room type
                type_filter = None if room_type == "All" else room_type
                
                rooms_df = retriever.get_rooms(
                    room_type=type_filter,
                    available_only=available_only,
                    limit=50
                )
                
                if rooms_df.empty:
                    return pd.DataFrame(columns=["Room Number", "Type", "Floor", "Beds", "Available"])
                
                # Format the data for display
                display_df = rooms_df[['room_number', 'room_type', 'floor_number', 'bed_capacity', 'available']].copy()
                display_df.columns = ["Room Number", "Type", "Floor", "Beds", "Available"]
                display_df['Available'] = display_df['Available'].apply(lambda x: "✅" if x else "❌")
                
                return display_df
            except Exception as e:
                logger.error(f"Error getting rooms: {e}")
                return pd.DataFrame(columns=["Room Number", "Type", "Floor", "Beds", "Available"])
        
        def get_equipment(available_only: bool):
            """Get medical equipment information"""
            try:
                retriever = get_data_retriever()
                equipment_df = retriever.get_medical_equipment(
                    available_only=available_only,
                    limit=50
                )
                
                if equipment_df.empty:
                    return pd.DataFrame(columns=["Equipment", "Category", "Available Qty", "Total Qty", "Location"])
                
                # Format the data for display
                display_df = equipment_df[['tool_name', 'category', 'quantity_available', 'quantity_total', 'location_description']].copy()
                display_df.columns = ["Equipment", "Category", "Available Qty", "Total Qty", "Location"]
                display_df = display_df.fillna("N/A")
                
                return display_df
            except Exception as e:
                logger.error(f"Error getting equipment: {e}")
                return pd.DataFrame(columns=["Equipment", "Category", "Available Qty", "Total Qty", "Location"])
        
        def get_staff(staff_type: str):
            """Get staff information"""
            try:
                retriever = get_data_retriever()
                
                # Filter by staff type
                type_filter = None if staff_type == "All" else staff_type
                
                staff_df = retriever.get_staff(staff_type=type_filter, limit=50)
                
                if staff_df.empty:
                    return pd.DataFrame(columns=["Name", "Role", "Staff Type", "Email"])
                
                # Format the data for display
                display_df = staff_df[['full_name', 'role', 'staff_type', 'email']].copy()
                display_df.columns = ["Name", "Role", "Staff Type", "Email"]
                display_df = display_df.fillna("N/A")
                
                return display_df
            except Exception as e:
                logger.error(f"Error getting staff: {e}")
                return pd.DataFrame(columns=["Name", "Role", "Staff Type", "Email"])
        
        # Connect event handlers
        refresh_btn.click(
            fn=check_database_connection,
            outputs=[connection_status, overview_display]
        )
        
        search_btn.click(
            fn=search_patients,
            inputs=[search_input],
            outputs=[patient_results]
        )
        
        search_input.submit(
            fn=search_patients,
            inputs=[search_input],
            outputs=[patient_results]
        )
        
        get_rooms_btn.click(
            fn=get_rooms,
            inputs=[room_type_filter, available_only_check],
            outputs=[room_results]
        )
        
        get_equipment_btn.click(
            fn=get_equipment,
            inputs=[equipment_available_only],
            outputs=[equipment_results]
        )
        
        get_staff_btn.click(
            fn=get_staff,
            inputs=[staff_type_filter],
            outputs=[staff_results]
        )
        
        # Initialize on load
        tab.load(
            fn=check_database_connection,
            outputs=[connection_status, overview_display]
        )
    
    return tab


def get_patient_summary_for_ai(patient_name: str) -> str:
    """
    Get patient summary for AI chat integration
    
    Args:
        patient_name: Name of the patient to search for
        
    Returns:
        str: Formatted patient summary
    """
    try:
        retriever = get_data_retriever()
        patients_df = retriever.search_patients_by_name(patient_name)
        
        if patients_df.empty:
            return f"No patients found with the name '{patient_name}'"
        
        # Format patient information
        summary = f"Found {len(patients_df)} patient(s) matching '{patient_name}':\n\n"
        
        for _, patient in patients_df.head(5).iterrows():
            summary += f"**{patient['full_name']}** (ID: {patient['id']})\n"
            summary += f"• DOB: {patient['date_of_birth']}\n"
            summary += f"• Blood Type: {patient['blood_group']}\n"
            summary += f"• Gender: {patient['gender']}\n"
            
            if patient['allergies'] and patient['allergies'] != 'None':
                summary += f"• Allergies: {patient['allergies']}\n"
            
            summary += "\n"
        
        return summary
    except Exception as e:
        logger.error(f"Error getting patient summary: {e}")
        return f"Error retrieving patient information: {str(e)}"


def get_room_availability_summary() -> str:
    """
    Get room availability summary for AI chat integration
    
    Returns:
        str: Formatted room availability summary
    """
    try:
        retriever = get_data_retriever()
        all_rooms_df = retriever.get_rooms()
        available_rooms_df = retriever.get_rooms(available_only=True)
        
        total_rooms = len(all_rooms_df)
        available_rooms = len(available_rooms_df)
        occupied_rooms = total_rooms - available_rooms
        
        summary = f"## Room Availability Summary\n\n"
        summary += f"• **Total Rooms:** {total_rooms}\n"
        summary += f"• **Available Rooms:** {available_rooms}\n"
        summary += f"• **Occupied Rooms:** {occupied_rooms}\n"
        summary += f"• **Occupancy Rate:** {(occupied_rooms/total_rooms*100):.1f}%\n\n"
        
        if not available_rooms_df.empty:
            summary += "**Available rooms by type:**\n"
            room_types = available_rooms_df['room_type'].value_counts()
            for room_type, count in room_types.items():
                summary += f"• {room_type}: {count} rooms\n"
        
        return summary
    except Exception as e:
        logger.error(f"Error getting room availability: {e}")
        return f"Error retrieving room availability: {str(e)}" 