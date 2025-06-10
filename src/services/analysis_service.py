"""
Analysis Service for Hospital AI Helper
Handles loading and processing of analysis result files when user queries contain @analysis
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service to handle analysis result files and questions"""
    
    def __init__(self):
        """Initialize the analysis service"""
        # Get project root and results directory
        project_root = Path(__file__).parent.parent.parent
        self.results_dir = project_root / "backend" / "result"
        
        # Analysis file mappings
        self.analysis_files = {
            "staffing": "staffing_result.json",
            "staff_load": "staff_load_result.json", 
            "staff_workload": "staff_load_result.json",
            "average_los": "average_los_result.json",
            "alos": "average_los_result.json",
            "length_of_stay": "average_los_result.json",
            "tool_utilisation": "tool_utilisation_result.json",
            "tool_utilization": "tool_utilisation_result.json",
            "equipment": "tool_utilisation_result.json",
            "inventory_expiry": "inventory_expiry_result.json",
            "expiry": "inventory_expiry_result.json",
            "census_forecast": "census_forecast_result.json",
            "bed_forecast": "census_forecast_result.json",
            "admission_split": "admission_split_result.json",
            "elective": "admission_split_result.json",
            "emergency": "admission_split_result.json",
            "los_prediction": "los_prediction_result.json",
            "burn_rate": "burn_rate_result.json",
            "consumption": "burn_rate_result.json",
            "usage": "burn_rate_result.json"
        }
        
        # Keywords for each analysis type
        self.analysis_keywords = {
            "staffing_result.json": [
                "staffing", "staff needs", "nurse", "doctor", "staff requirements", 
                "workforce", "staff forecast", "nursing staff"
            ],
            "staff_load_result.json": [
                "staff load", "workload", "patient assignments", "staff burden",
                "staff capacity", "overworked", "staff utilization"
            ],
            "average_los_result.json": [
                "length of stay", "los", "alos", "average stay", "ward statistics",
                "discharge", "patient stay", "bed days"
            ],
            "tool_utilisation_result.json": [
                "tool utilization", "equipment", "devices", "medical tools",
                "infusion pump", "ventilator", "defibrillator", "monitoring"
            ],
            "inventory_expiry_result.json": [
                "expiry", "inventory", "blood units", "expired", "consumables",
                "blood bank", "medical supplies", "expiration"
            ],
            "census_forecast_result.json": [
                "bed census", "bed forecast", "bed occupancy", "capacity",
                "bed utilization", "bed availability", "census"
            ],
            "admission_split_result.json": [
                "admission", "elective", "emergency", "admission type",
                "planned", "urgent", "admission pattern"
            ],
            "los_prediction_result.json": [
                "los prediction", "stay prediction", "discharge prediction",
                "length prediction", "expected stay"
            ],
            "burn_rate_result.json": [
                "burn rate", "consumption", "usage rate", "inventory usage",
                "supply consumption", "consumption forecast"
            ]
        }

    def is_analysis_query(self, message: str) -> bool:
        """Check if the message contains @analysis"""
        return "@analysis" in message.lower()

    def determine_relevant_analyses(self, message: str) -> List[str]:
        """Determine which analysis files are relevant to the user's question"""
        message_lower = message.lower()
        relevant_files = []
        
        # Check direct file mentions in analysis_files mapping
        for keyword, filename in self.analysis_files.items():
            if keyword in message_lower:
                if filename not in relevant_files:
                    relevant_files.append(filename)
        
        # Check keyword matches
        for filename, keywords in self.analysis_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    if filename not in relevant_files:
                        relevant_files.append(filename)
                    break
        
        # If no specific analysis detected, return all available files
        if not relevant_files:
            relevant_files = list(self.analysis_files.values())
            # Remove duplicates while preserving order
            relevant_files = list(dict.fromkeys(relevant_files))
        
        return relevant_files

    def load_analysis_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a specific analysis result file"""
        try:
            file_path = self.results_dir / filename
            if not file_path.exists():
                logger.warning(f"Analysis file not found: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
                
        except Exception as e:
            logger.error(f"Error loading analysis file {filename}: {e}")
            return None

    def format_analysis_data(self, filename: str, data: Dict[str, Any]) -> str:
        """Format analysis data for AI consumption"""
        if not data:
            return f"Analysis data from {filename} could not be loaded."
        
        try:
            analysis_id = data.get("analysis_id", "unknown")
            timestamp = data.get("generated_at", "unknown")
            
            formatted = f"## Analysis: {analysis_id.upper().replace('_', ' ')}\n"
            formatted += f"**Generated:** {timestamp}\n\n"
            
            # Format based on analysis type
            if "staffing" in filename:
                return self._format_staffing_data(data, formatted)
            elif "staff_load" in filename:
                return self._format_staff_load_data(data, formatted)
            elif "average_los" in filename:
                return self._format_los_data(data, formatted)
            elif "tool_utilisation" in filename:
                return self._format_tool_data(data, formatted)
            elif "inventory_expiry" in filename:
                return self._format_inventory_data(data, formatted)
            elif "census_forecast" in filename:
                return self._format_census_data(data, formatted)
            elif "admission_split" in filename:
                return self._format_admission_data(data, formatted)
            elif "los_prediction" in filename:
                return self._format_prediction_data(data, formatted)
            elif "burn_rate" in filename:
                return self._format_burn_rate_data(data, formatted)
            else:
                return formatted + f"**Raw Data:**\n```json\n{json.dumps(data, indent=2)[:1000]}...\n```"
                
        except Exception as e:
            logger.error(f"Error formatting analysis data: {e}")
            return f"Error formatting analysis data from {filename}: {str(e)}"

    def _format_staffing_data(self, data: Dict[str, Any], base: str) -> str:
        """Format staffing analysis data"""
        staff_data = data.get("data", {})
        current_staff = staff_data.get("current_staff", {})
        recommendations = staff_data.get("recommendations", [])
        
        formatted = base
        formatted += f"**Current Staff:** {current_staff.get('total_staff', 0)} total\n"
        formatted += f"- Nurses: {current_staff.get('by_type', {}).get('nurses', 0)}\n"
        formatted += f"- Doctors: {current_staff.get('by_type', {}).get('doctors', 0)}\n\n"
        
        if recommendations:
            formatted += "**Recommendations:**\n"
            for rec in recommendations:
                formatted += f"- {rec.get('message', 'No message')}\n"
        
        return formatted

    def _format_staff_load_data(self, data: Dict[str, Any], base: str) -> str:
        """Format staff load analysis data"""
        staff_data = data.get("data", {})
        top_staff = staff_data.get("top_staff", [])
        summary = staff_data.get("summary_statistics", {})
        
        formatted = base
        formatted += f"**Summary:**\n"
        formatted += f"- Total Active Staff: {summary.get('total_active_staff', 0)}\n"
        formatted += f"- Average Assignments per Staff: {summary.get('avg_assignments_per_staff', 0):.1f}\n"
        formatted += f"- Max Assignments: {summary.get('max_assignments', 0)}\n\n"
        
        if top_staff:
            formatted += "**Top Loaded Staff:**\n"
            for staff in top_staff[:5]:
                formatted += f"- {staff.get('full_name', 'Unknown')}: {staff.get('patient_assignments', 0)} assignments ({staff.get('workload_level', 'normal')})\n"
        
        return formatted

    def _format_los_data(self, data: Dict[str, Any], base: str) -> str:
        """Format length of stay analysis data"""
        ward_stats = data.get("data", {}).get("ward_statistics", [])
        overall = data.get("data", {}).get("overall_statistics", {})
        
        formatted = base
        formatted += f"**Overall Statistics:**\n"
        formatted += f"- Average LOS: {overall.get('overall_avg_los', 0):.2f} days\n"
        formatted += f"- Total Completed Stays: {overall.get('total_completed_stays', 0)}\n\n"
        
        if ward_stats:
            formatted += "**By Ward Type:**\n"
            for ward in ward_stats:
                formatted += f"- {ward.get('ward_type', 'Unknown')}: {ward.get('avg_los_days', 0):.2f} days (median: {ward.get('median_los_days', 0):.1f})\n"
        
        return formatted

    def _format_tool_data(self, data: Dict[str, Any], base: str) -> str:
        """Format tool utilization data"""
        top_tools = data.get("data", {}).get("top_tools", [])
        summary = data.get("data", {}).get("summary_statistics", {})
        
        formatted = base
        formatted += f"**Summary:**\n"
        formatted += f"- Total Tools: {summary.get('total_tools', 0)}\n"
        formatted += f"- Average Utilization: {summary.get('avg_utilisation', 0):.1f}%\n"
        formatted += f"- Low Utilization Tools: {summary.get('low_util_tools', 0)}\n\n"
        
        if top_tools:
            formatted += "**Tool Status (Top 10):**\n"
            for tool in top_tools[:10]:
                formatted += f"- {tool.get('tool_name', 'Unknown')}: {tool.get('util_pct', 0):.1f}% ({tool.get('status', 'unknown')})\n"
        
        return formatted

    def _format_inventory_data(self, data: Dict[str, Any], base: str) -> str:
        """Format inventory expiry data"""
        expiring_items = data.get("data", {}).get("expiring_items", [])
        summary = data.get("data", {}).get("summary_statistics", {})
        alerts = data.get("data", {}).get("alerts", [])
        
        formatted = base
        formatted += f"**Summary:**\n"
        formatted += f"- Total Items: {summary.get('total_inventory_items', 0)}\n"
        formatted += f"- Items Expiring Soon: {summary.get('items_expiring_within_threshold', 0)}\n"
        formatted += f"- Critical Items: {summary.get('critical_items', 0)}\n"
        formatted += f"- Urgent Items: {summary.get('urgent_items', 0)}\n\n"
        
        if alerts:
            formatted += "**Alerts:**\n"
            for alert in alerts:
                formatted += f"- {alert.get('level', 'info').upper()}: {alert.get('message', 'No message')}\n"
            formatted += "\n"
        
        if expiring_items:
            formatted += "**Items Expiring Soon:**\n"
            for item in expiring_items[:10]:
                formatted += f"- {item.get('item_name', 'Unknown')}: {item.get('days_to_expiry', 0)} days ({item.get('urgency', 'normal')})\n"
        
        return formatted

    def _format_census_data(self, data: Dict[str, Any], base: str) -> str:
        """Format census forecast data"""
        forecast = data.get("data", {}).get("forecast", [])
        model_info = data.get("data", {}).get("model_info", {})
        
        formatted = base
        formatted += f"**Model Info:**\n"
        formatted += f"- Method: {model_info.get('method', 'unknown')}\n"
        formatted += f"- Total Capacity: {model_info.get('total_capacity', 0)} beds\n"
        formatted += f"- Forecast Days: {model_info.get('forecast_days', 0)}\n\n"
        
        if forecast:
            formatted += "**Forecast:**\n"
            for day in forecast:
                formatted += f"- {day.get('date', 'Unknown')}: {day.get('predicted_occupied_beds', 0)} beds ({day.get('utilisation_pct', 0):.1f}%)\n"
        
        return formatted

    def _format_admission_data(self, data: Dict[str, Any], base: str) -> str:
        """Format admission split data"""
        period = data.get("data", {}).get("analysis_period", {})
        summary = data.get("data", {}).get("summary_stats", {})
        
        formatted = base
        formatted += f"**Analysis Period:**\n"
        formatted += f"- Days Analyzed: {period.get('days_analyzed', 0)}\n"
        formatted += f"- Total Admissions: {period.get('total_admissions', 0)}\n\n"
        
        formatted += f"**Daily Averages:**\n"
        formatted += f"- Elective: {summary.get('avg_daily_elective', 0):.1f}\n"
        formatted += f"- Emergency: {summary.get('avg_daily_emergency', 0):.1f}\n"
        
        return formatted

    def _format_prediction_data(self, data: Dict[str, Any], base: str) -> str:
        """Format LOS prediction data"""
        ward_stats = data.get("data", {}).get("ward_statistics", [])
        overall = data.get("data", {}).get("overall_statistics", {})
        
        formatted = base
        formatted += f"**Prediction Model Available:** {data.get('data', {}).get('model_available', False)}\n\n"
        
        formatted += f"**Overall Statistics:**\n"
        formatted += f"- Average LOS: {overall.get('overall_avg_los', 0):.2f} days\n"
        formatted += f"- Total Stays: {overall.get('total_completed_stays', 0)}\n\n"
        
        if ward_stats:
            formatted += "**By Ward (for prediction reference):**\n"
            for ward in ward_stats:
                formatted += f"- {ward.get('ward_type', 'Unknown')}: {ward.get('avg_los_days', 0):.2f} days\n"
        
        return formatted

    def _format_burn_rate_data(self, data: Dict[str, Any], base: str) -> str:
        """Format burn rate data"""
        summary = data.get("data", {}).get("summary", {})
        items = data.get("data", {}).get("items", [])
        
        formatted = base
        formatted += f"**Summary:**\n"
        formatted += f"- Total Items: {summary.get('total_items', 0)}\n"
        formatted += f"- Critical Items: {summary.get('critical_items', 0)}\n"
        formatted += f"- Low Stock Items: {summary.get('low_stock_items', 0)}\n\n"
        
        # Show items with highest usage rates
        if items:
            high_usage = sorted(items, key=lambda x: x.get('daily_usage_rate', 0), reverse=True)[:5]
            formatted += "**Highest Usage Items:**\n"
            for item in high_usage:
                formatted += f"- {item.get('item_name', 'Unknown')}: {item.get('daily_usage_rate', 0):.3f}/day\n"
        
        return formatted

    def process_analysis_query(self, user_message: str) -> str:
        """Process a user query about analysis data"""
        try:
            # Remove @analysis from the message for cleaner processing
            clean_message = user_message.replace("@analysis", "").strip()
            
            # Determine relevant analyses
            relevant_files = self.determine_relevant_analyses(user_message)
            
            if not relevant_files:
                return "No relevant analysis files found for your query."
            
            # Load and format analysis data
            analysis_context = "# Hospital Analysis Data\n\n"
            
            for filename in relevant_files:
                data = self.load_analysis_file(filename)
                if data:
                    formatted_data = self.format_analysis_data(filename, data)
                    analysis_context += formatted_data + "\n\n"
            
            # Create enhanced prompt for AI
            enhanced_prompt = f"""
User Question: {clean_message}

Analysis Data Context:
{analysis_context}

INSTRUCTIONS: The user is asking about hospital analysis data. Please provide:

1. **Direct Answer**: Address their specific question using the analysis data provided
2. **Key Insights**: Highlight the most relevant findings from the analysis
3. **Medical Context**: Provide professional interpretation of the data
4. **Recommendations**: Suggest actionable insights based on the analysis

Use LaTeX formatting for any numerical data, percentages, or calculations.
Format your response in a clear, professional manner with proper headers and bullet points.
"""
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error processing analysis query: {e}")
            return f"Error processing analysis query: {str(e)}"


# Global instance
analysis_service = AnalysisService()