import asyncio
import time
from typing import Any, Dict, List

import gradio as gr

from ..models.mcp_handler import MCPHandler
from ..models.nebius_model import NebiusModel
from ..utils.helpers import process_user_input
from ..utils.latex_formatter import format_medical_response
import os


def create_main_interface(config: Dict[str, Any]) -> gr.Blocks:
    """
    Create a modern hospital dashboard Gradio interface for the MCP HF Hackathon application

    Args:
        config: Configuration dictionary

    Returns:
        gr.Blocks: The modern hospital dashboard Gradio interface
    """
    # Initialize MCP handler and Nebius model
    mcp_handler = MCPHandler(config)
    nebius_model = NebiusModel()

    # Get the root directory (go up 2 levels from src/components/interface.py)
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    css_file = os.path.join(root_dir, "static", "css", "styles.css")

    # Read CSS content from external file
    try:
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
    except FileNotFoundError:
        print(
            f"Warning: CSS file not found at {css_file}, using embedded CSS as fallback"
        )
        css_content = load_modern_hospital_css()

    with gr.Blocks(
        title="Health AI Hospital Aid (H.A.H.A)",
        css=css_content,
        fill_height=True,
        head=load_latex_scripts(),
    ) as demo:

        # Main container with fixed layout
        with gr.Row(elem_classes="main-container", equal_height=True):

            # Left Sidebar - Chat Panel
            with gr.Column(scale=1, min_width=350, elem_classes="sidebar-container"):

                # Assistant Header - Compact
                gr.HTML(
                    """
                <div class="assistant-header">
                    <div class="avatar-circle">🩺</div>
                    <div class="assistant-text">
                        <h3>Medical Assistant</h3>
                        <p>How can I help you?</p>
                    </div>
                </div>
                """
                )  # Chat Interface - Normal Chat
                chatbot = gr.Chatbot(
                    type="messages",
                    height=600,
                    show_copy_button=False,
                    show_share_button=True,
                    container=False,
                    layout="bubble",
                    elem_classes="chatbot-gr-chatbot",
                )  # Chat Input Area - Standard
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask about hospital status, patients, or medical queries...",
                        show_label=False,
                        lines=1,
                        max_lines=3,
                        container=False,
                        scale=4,
                    )
                    send_btn = gr.Button(
                        "→", size="sm", scale=0, min_width=40
                    )  # Test Section with Dropdown
                with gr.Row(elem_classes="tools-section"):
                    with gr.Column(scale=1):
                        test_dropdown = gr.Dropdown(
                            choices=["Main Chat", "Visualize"],
                            label="",
                            value="Main Chat",
                            interactive=True,
                            container=True,
                            elem_classes="custom-test-dropdown",
                            show_label=False,
                        )

                # Guidance text from image
                """ gr.HTML( """
                """
                <div class="guidance-text">
                    <p>I'll assist you with health information and guidance. If you have any health-related questions or concerns, feel free to ask, and I'll do my best to assist you. Remember, I'm not a replacement for professional medical advice, and it's always best to consult with a healthcare professional for serious concerns.</p>
                    <br>
                    <p>What's on your mind today? Do you have a specific health topic you'd like to discuss or any questions about general medicine?</p>
                </div>
                """
            """     ) """

            # Right Side - Dashboard
            with gr.Column(scale=2, elem_classes="dashboard-container"):

                # Dashboard Header - Compact
                with gr.Row(elem_classes="dashboard-header-compact"):
                    with gr.Column():
                        gr.HTML(
                            """
                        <div class="dashboard-title-compact">
                            <h1>Health AI Hospital Aid (H.A.H.A)</h1>
                            <p>Medical Assistant</p>
                        </div>
                        """
                        )

                    with gr.Column(scale=1, elem_classes="dashboard-controls-compact"):
                        # Helpline Button
                        helpline_btn = gr.Button(
                            "📞 Helpline",
                            elem_classes="helpline-btn-compact",
                            size="sm",
                            scale=1,
                        )

                # Main Content Area - Navigation and Sections
                with gr.Column(elem_classes="main-content-area"):
                    # Navigation Buttons
                    gr.HTML(
                        """
                        <div class="nav-buttons-container">
                            <button class="nav-btn active" data-section="dashboard">Dashboard</button>
                            <button class="nav-btn" data-section="data">Data</button>
                        </div>
                        """
                    )

                    # Dashboard Section (with charts and controls)
                    gr.HTML(
                        """
                        <div id="dashboard-section" class="dashboard-section" style="display: block;">
                            <h2 class="analysis-title">Dashboard Analytics</h2>
                            <div class="analysis-selector-container">
                                <select class="analysis-selector" name="analysis-selector" id="analysis-selector">
                                    <option value="bed-occupancy">Real-time bed occupancy by ward & ICU</option>
                                    <option value="alos">Average Length-of-Stay (ALOS) by procedure / ward</option>
                                    <option value="staff-workload">Staff workload dashboard</option>
                                    <option value="tool-utilisation">Tool utilisation & idle time</option>
                                    <option value="inventory-expiry">Inventory expiry radar</option>
                                    <option value="bed-census">Short-horizon bed census</option>
                                    <option value="elective-emergency">Elective vs emergency</option>
                                    <option value="los-prediction">Length-of-stay prediction</option>
                                </select>
                                <div class="selector-icon">▼</div>
                            </div>
                        
                            <!-- Chart Type Controls -->
                            <div class="chart-controls">
                                <button class="chart-btn active" data-chart="line">Line</button>
                                <button class="chart-btn" data-chart="bar">Bar</button>
                                <button class="chart-btn" data-chart="pie">Pie</button>
                                <button class="chart-btn" data-chart="scatter">Scatter</button>
                            </div>
                                
                            <!-- Chart Container -->
                            <div class="chart-container">
                                <div class="chart-legend">
                                    <span class="legend-item">
                                        <span class="legend-color" style="background: #3b82f6;"></span>
                                        Patient Count
                                    </span>
                                    <span class="legend-item">
                                        <span class="legend-color" style="background: #22d3ee;"></span>
                                        Revenue Data
                                    </span>
                                </div>
                                    
                                <div class="line-chart">
                                    <svg width="100%" height="400" viewBox="0 0 600 300">
                                        <!-- Grid lines -->
                                        <defs>
                                            <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                                                <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                                            </pattern>
                                        </defs>
                                        <rect width="100%" height="100%" fill="url(#grid)" />
                                        
                                        <!-- Y-axis labels -->
                                        <text x="30" y="50" fill="#64748b" font-size="12" text-anchor="end">65</text>
                                        <text x="30" y="88" fill="#64748b" font-size="12" text-anchor="end">60</text>
                                        <text x="30" y="125" fill="#64748b" font-size="12" text-anchor="end">55</text>
                                        <text x="30" y="163" fill="#64748b" font-size="12" text-anchor="end">50</text>
                                        <text x="30" y="200" fill="#64748b" font-size="12" text-anchor="end">45</text>
                                        <text x="30" y="238" fill="#64748b" font-size="12" text-anchor="end">40</text>
                                        
                                        <!-- X-axis labels -->
                                        <text x="80" y="280" fill="#64748b" font-size="12" text-anchor="middle">January</text>
                                        <text x="160" y="280" fill="#64748b" font-size="12" text-anchor="middle">February</text>
                                        <text x="240" y="280" fill="#64748b" font-size="12" text-anchor="middle">March</text>
                                        <text x="320" y="280" fill="#64748b" font-size="12" text-anchor="middle">April</text>
                                        <text x="400" y="280" fill="#64748b" font-size="12" text-anchor="middle">May</text>
                                        <text x="480" y="280" fill="#64748b" font-size="12" text-anchor="middle">June</text>
                                        <text x="560" y="280" fill="#64748b" font-size="12" text-anchor="middle">July</text>
                                        
                                        <!-- Red line (declining) -->
                                        <path d="M 80 50 L 160 88 L 240 125 L 320 163 L 400 200 L 480 163 L 560 238" 
                                              stroke="#ef4444" stroke-width="3" fill="none" stroke-linecap="round"/>
                                        
                                        <!-- Cyan/Teal line (rising then declining) -->
                                        <path d="M 80 238 L 160 225 L 240 200 L 320 175 L 400 138 L 480 125 L 560 163" 
                                              stroke="#22d3ee" stroke-width="3" fill="none" stroke-linecap="round"/>
                                        
                                        <!-- Gray dotted line -->
                                        <path d="M 80 88 L 160 125 L 240 138 L 320 150 L 400 175 L 480 188 L 560 200" 
                                              stroke="#94a3b8" stroke-width="2" fill="none" stroke-dasharray="5,5"/>
                                        
                                        <!-- Data points -->
                                        <circle cx="80" cy="50" r="4" fill="#ef4444"/>
                                        <circle cx="160" cy="88" r="4" fill="#ef4444"/>
                                        <circle cx="240" cy="125" r="4" fill="#ef4444"/>
                                        <circle cx="320" cy="163" r="4" fill="#ef4444"/>
                                        <circle cx="400" cy="200" r="4" fill="#ef4444"/>
                                        <circle cx="480" cy="163" r="4" fill="#ef4444"/>
                                        <circle cx="560" cy="238" r="4" fill="#ef4444"/>
                                        
                                        <circle cx="80" cy="238" r="4" fill="#22d3ee"/>
                                        <circle cx="160" cy="225" r="4" fill="#22d3ee"/>
                                        <circle cx="240" cy="200" r="4" fill="#22d3ee"/>
                                        <circle cx="320" cy="175" r="4" fill="#22d3ee"/>
                                        <circle cx="400" cy="138" r="4" fill="#22d3ee"/>
                                        <circle cx="480" cy="125" r="4" fill="#22d3ee"/>
                                        <circle cx="560" cy="163" r="4" fill="#22d3ee"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                        """
                    )

                    # Data Section (separate component without charts)
                    gr.HTML(
                        """
                        <div id="data-section" class="data-section" style="display: none;">
                            <div class="data-component">
                                <div class="data-header">
                                    <h2>Data Management</h2>
                                    <p>Manage and view hospital data records</p>
                                </div>
                                
                                <div class="data-content">
                                    <div class="data-tabs">
                                        <button class="data-tab active" data-tab="patients">Patients</button>
                                        <button class="data-tab" data-tab="staff">Staff</button>
                                        <button class="data-tab" data-tab="rooms">Rooms</button>
                                        <button class="data-tab" data-tab="equipment">Equipment</button>
                                    </div>
                                    
                                    <div class="data-table-container">
                                        <div id="patients-data" class="data-table-section active">
                                            <h3>Patient Records</h3>
                                            <div class="data-table">
                                                <div class="table-header">
                                                    <span>ID</span>
                                                    <span>Name</span>
                                                    <span>Age</span>
                                                    <span>Room</span>
                                                    <span>Status</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>P001</span>
                                                    <span>John Smith</span>
                                                    <span>45</span>
                                                    <span>101</span>
                                                    <span class="status-active">Active</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>P002</span>
                                                    <span>Emma Johnson</span>
                                                    <span>32</span>
                                                    <span>205</span>
                                                    <span class="status-discharged">Discharged</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>P003</span>
                                                    <span>Michael Brown</span>
                                                    <span>67</span>
                                                    <span>150</span>
                                                    <span class="status-active">Active</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div id="staff-data" class="data-table-section" style="display: none;">
                                            <h3>Staff Records</h3>
                                            <div class="data-table">
                                                <div class="table-header">
                                                    <span>ID</span>
                                                    <span>Name</span>
                                                    <span>Role</span>
                                                    <span>Department</span>
                                                    <span>Status</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>S001</span>
                                                    <span>Dr. Sarah Wilson</span>
                                                    <span>Doctor</span>
                                                    <span>Cardiology</span>
                                                    <span class="status-active">On Duty</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>S002</span>
                                                    <span>Nurse Linda Davis</span>
                                                    <span>Nurse</span>
                                                    <span>Emergency</span>
                                                    <span class="status-active">On Duty</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div id="rooms-data" class="data-table-section" style="display: none;">
                                            <h3>Room Management</h3>
                                            <div class="data-table">
                                                <div class="table-header">
                                                    <span>Room</span>
                                                    <span>Type</span>
                                                    <span>Occupancy</span>
                                                    <span>Status</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>101</span>
                                                    <span>General</span>
                                                    <span>1/2</span>
                                                    <span class="status-active">Available</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>205</span>
                                                    <span>Private</span>
                                                    <span>0/1</span>
                                                    <span class="status-discharged">Empty</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div id="equipment-data" class="data-table-section" style="display: none;">
                                            <h3>Equipment Status</h3>
                                            <div class="data-table">
                                                <div class="table-header">
                                                    <span>ID</span>
                                                    <span>Equipment</span>
                                                    <span>Location</span>
                                                    <span>Status</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>E001</span>
                                                    <span>MRI Scanner</span>
                                                    <span>Radiology</span>
                                                    <span class="status-active">Operational</span>
                                                </div>
                                                <div class="table-row">
                                                    <span>E002</span>
                                                    <span>X-Ray Machine</span>
                                                    <span>Emergency</span>
                                                    <span class="status-active">Operational</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                    )
        # Hidden status indicator
        status = gr.Textbox(visible=False)

        # Event handlers
        def respond(
            message: str,
            history: List[Dict],
            model: str,
            temp: float,
            max_tok: int,
            specialty: str,
            context: str,
        ):
            """Handle user message and generate AI response"""
            if not message.strip():
                return history, ""

            # Add user message to history
            history.append({"role": "user", "content": message})

            # Generate AI response using the selected model
            bot_response = handle_ai_response(
                message, model, temp, max_tok, specialty, context
            )

            # Add AI response to history
            history.append({"role": "assistant", "content": bot_response})

            return history, ""

        def clear_conversation():
            """Clear the conversation history"""
            return []

        def stream_response(
            message: str,
            history: List[Dict],
            model: str,
            temp: float,
            max_tok: int,
            specialty: str,
            context: str,
        ):
            """Stream AI response for real-time effect with loading indicators"""
            if not message.strip():
                yield history, ""
                return

            # Add user message
            history.append({"role": "user", "content": message})
            yield history, ""

            # Add initial loading message with animated dots
            loading_states = [
                "🤔 Thinking...",
                "🔍 Analyzing your request...",
                "🏥 Checking hospital systems...",
                "⚡ Processing with AI...",
            ]

            # Start with first loading state
            history.append(
                {
                    "role": "assistant",
                    "content": f'<div class="loading-indicator" aria-live="polite" role="status" data-type="thinking">{loading_states[0]}<span class="loading-dots"></span></div>',
                }
            )
            yield history, ""

            # Cycle through loading states briefly
            import time

            for i, loading_text in enumerate(loading_states[:3]):
                time.sleep(0.4)
                data_type = "thinking" if i < 2 else "ai"
                history[-1][
                    "content"
                ] = f'<div class="loading-indicator" aria-live="polite" role="status" data-type="{data_type}">{loading_text}<span class="loading-dots"></span></div>'
                yield history, ""

            # Check if this is a database query first
            try:
                from ..services.advanced_database_mcp import advanced_database_mcp

                # First check if it's a database-related query
                if any(
                    keyword in message.lower()
                    for keyword in [
                        "patient",
                        "room",
                        "nurse",
                        "doctor",
                        "staff",
                        "equipment",
                        "medical",
                        "hospital",
                        "bed",
                        "top",
                        "list",
                        "statistics",
                        "occupancy",
                        "inventory",
                        "history",
                        "admission",
                    ]
                ):
                    # Show database-specific loading state
                    history[-1][
                        "content"
                    ] = f'<div class="loading-indicator" aria-live="polite" role="status" data-type="database">🗄️ Querying the database...<span class="loading-dots"></span></div>'
                    yield history, ""
                    time.sleep(0.5)

                    # Process with advanced database capabilities
                    db_response = advanced_database_mcp.process_advanced_query(message)

                    # If we got real data from the database, pass it through AI for analysis
                    if (
                        "Error processing" not in db_response
                        and "Use more specific queries" not in db_response
                    ):
                        # Show AI analysis loading state
                        history[-1][
                            "content"
                        ] = f'<div class="loading-indicator" aria-live="polite" role="status" data-type="ai">🧠 Analyzing results with AI...<span class="loading-dots"></span></div>'
                        yield history, ""
                        time.sleep(0.3)

                        # Create enhanced prompt for AI analysis
                        enhanced_prompt = f"""
User Question: {message}

Database Results: 
{db_response}

IMPORTANT: The user specifically requested details/information. Please provide:

1. FIRST: Present the complete data the user requested in a well-formatted, easy-to-read manner
   - Include ALL patient details in a structured format
   - Use proper formatting with line breaks, headers, and organization
   - Format medical values with LaTeX (ages, blood pressure, dosages, etc.)

2. SECOND: After presenting the complete data, provide your professional medical analysis including:
   - Key insights and patterns
   - Medical observations and recommendations
   - Data quality issues or notable findings

Make sure the user gets both the complete information they requested AND your professional analysis.
"""

                        # Use AI to analyze the database results instead of returning raw data
                        if (
                            model == "nebius-llama-3.3-70b"
                            and nebius_model.is_available()
                        ):
                            # Clear loading indicator and start real response
                            history[-1]["content"] = ""

                            try:
                                response_generator = nebius_model.generate_response(
                                    prompt=enhanced_prompt,
                                    context=f"Database query results included in the analysis",
                                    specialty="General Medicine",
                                    max_tokens=max(
                                        1000, 2000
                                    ),  # Ensure enough space for complete data + analysis
                                    temperature=0.4,
                                    stream=True,
                                )

                                for chunk in response_generator:
                                    if chunk:
                                        history[-1]["content"] += chunk
                                        yield history, ""

                            except Exception as e:
                                error_msg = (
                                    f"❌ Error analyzing database results: {str(e)}"
                                )
                                history[-1]["content"] = error_msg
                                yield history, ""
                        else:
                            # Fallback: use handle_ai_response for analysis
                            analyzed_response = handle_ai_response(
                                enhanced_prompt,
                                model,
                                0.4,
                                max(1000, 2000),
                                "General Medicine",
                                f"Database query results included in the analysis",
                            )
                            # Clear loading indicator and start real response
                            history[-1]["content"] = ""

                            # Stream the analyzed response
                            words = analyzed_response.split()
                            for i, word in enumerate(words):
                                if i == 0:
                                    history[-1]["content"] = word
                                else:
                                    history[-1]["content"] += " " + word
                                time.sleep(0.02)
                                yield history, ""
                        return

            except Exception as e:
                # If advanced database integration fails, continue with regular AI response
                pass

            # Check if using Nebius model and if it's available
            if model == "nebius-llama-3.3-70b" and nebius_model.is_available():
                # Show final loading state for AI generation
                history[-1][
                    "content"
                ] = f'<div class="loading-indicator" aria-live="polite" role="status" data-type="generating">🚀 Generating response...<span class="loading-dots"></span></div>'
                yield history, ""
                time.sleep(0.3)

                # Clear loading indicator and start real response
                history[-1]["content"] = ""

                try:
                    response_generator = nebius_model.generate_response(
                        prompt=message,
                        context=None,
                        specialty="General Medicine",
                        max_tokens=1000,
                        temperature=0.4,
                        stream=True,
                    )

                    for chunk in response_generator:
                        if chunk:
                            history[-1]["content"] += chunk
                            yield history, ""

                except Exception as e:
                    error_msg = f"❌ Nebius API Error: {str(e)}\n\nPlease check your API key configuration."
                    history[-1]["content"] = error_msg
                    yield history, ""
            else:
                # Show final loading state for fallback response
                history[-1][
                    "content"
                ] = f'<div class="loading-indicator" aria-live="polite" role="status" data-type="generating">🤖 Preparing response...<span class="loading-dots"></span></div>'
                yield history, ""
                time.sleep(0.4)

                # Use fallback response (simulate streaming)
                response = handle_ai_response(
                    message, model, 0.4, 1000, "General Medicine", ""
                )
                # Clear loading indicator and start real response
                history[-1]["content"] = ""

                # Stream the response word by word
                words = response.split()
                for i, word in enumerate(words):
                    if i == 0:
                        history[-1]["content"] = word
                    else:
                        history[-1]["content"] += " " + word
                    time.sleep(0.05)  # Simulate streaming delay
                    yield history, ""  # Quick action handler

        def handle_helpline():
            return "", [
                {
                    "role": "user",
                    "content": "Connect me to the hospital helpline for urgent assistance",
                },
                {
                    "role": "assistant",
                    "content": "📞 The helpline number of the hospital is **555-HELP (555-4357)**.\n\nOur helpline is available 24/7 for urgent assistance. Please call immediately if you have any medical emergencies or need immediate support.",
                },
            ]

        # Chat state management
        original_chat_state = gr.State([])  # Store original chat history
        visualize_chat_state = gr.State([])  # Store visualize chat history
        current_mode_state = gr.State(
            "original"
        )  # Track current mode: "original" or "visualize"

        # Wrapper function to handle state management for streaming
        def stream_response_with_state(
            message: str,
            history: List[Dict],
            model: str,
            temp: float,
            max_tok: int,
            specialty: str,
            context: str,
            original_chat,
            visualize_chat,
            current_mode,
        ):
            """Stream response and update appropriate chat state"""
            # Use the existing stream_response function
            for updated_history, cleared_input in stream_response(
                message, history, model, temp, max_tok, specialty, context
            ):
                # Update the appropriate chat state based on current mode
                if current_mode == "visualize":
                    new_visualize_chat = updated_history
                    new_original_chat = original_chat
                else:
                    new_original_chat = updated_history
                    new_visualize_chat = visualize_chat

                yield updated_history, cleared_input, new_original_chat, new_visualize_chat, current_mode

        # Connect events for sidebar chat with state management
        msg.submit(
            fn=stream_response_with_state,
            inputs=[
                msg,
                chatbot,
                gr.State("nebius-llama-3.3-70b"),  # default model
                gr.State(0.4),  # temperature
                gr.State(1000),  # max_tokens
                gr.State("General Medicine"),  # medical_specialty
                gr.State(""),  # context_input
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
            outputs=[
                chatbot,
                msg,
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
            show_progress="hidden",
        )

        send_btn.click(
            fn=stream_response_with_state,
            inputs=[
                msg,
                chatbot,
                gr.State("nebius-llama-3.3-70b"),  # default model
                gr.State(0.4),  # temperature
                gr.State(1000),  # max_tokens
                gr.State("General Medicine"),  # medical_specialty
                gr.State(""),  # context_input
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
            outputs=[
                chatbot,
                msg,
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
            show_progress="hidden",
        )  # Update helpline handler to work with state management

        def handle_helpline_with_state(original_chat, visualize_chat, current_mode):
            """Handle helpline with state management"""
            helpline_response = [
                {
                    "role": "user",
                    "content": "Connect me to the hospital helpline for urgent assistance",
                },
                {
                    "role": "assistant",
                    "content": "📞 The helpline number of the hospital is **555-HELP (555-4357)**.\n\nOur helpline is available 24/7 for urgent assistance. Please call immediately if you have any medical emergencies or need immediate support.",
                },
            ]

            # Update the appropriate chat state
            if current_mode == "visualize":
                new_visualize_chat = visualize_chat + helpline_response
                new_original_chat = original_chat
                new_chat_display = new_visualize_chat
            else:
                new_original_chat = original_chat + helpline_response
                new_visualize_chat = visualize_chat
                new_chat_display = new_original_chat

            return (
                "",
                new_chat_display,
                new_original_chat,
                new_visualize_chat,
                current_mode,
            )

        helpline_btn.click(
            fn=handle_helpline_with_state,
            inputs=[original_chat_state, visualize_chat_state, current_mode_state],
            outputs=[
                msg,
                chatbot,
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
        )

        # Test dropdown handler
        def handle_tool_selection(
            tool_name, current_chat, original_chat, visualize_chat, current_mode
        ):
            """Handle tool selection from dropdown with separate chat flows"""
            if not tool_name:
                return "", current_chat, original_chat, visualize_chat, current_mode

            if tool_name == "Main Chat":
                # Return to original chat with full history intact
                # Show welcome back message only if there's existing chat history
                if original_chat:
                    display_chat = original_chat + [
                        {
                            "role": "assistant",
                            "content": "--- 🔄 **Welcome back to the main chat!**\n\n📋 You can see your previous conversation history above, but please note that I'm starting with a fresh conversation context. I don't have access to the details from our previous messages, so feel free to provide any relevant context if you'd like to continue where we left off.\n\nHow can I assist you today?",
                        }
                    ]
                    stored_original_chat = (
                        original_chat  # Keep original history without welcome message
                    )
                else:
                    display_chat = original_chat
                    stored_original_chat = original_chat
                return (
                    "",
                    display_chat,
                    stored_original_chat,
                    visualize_chat,
                    "original",
                )

            elif tool_name == "Visualize":
                # Switch to visualize mode
                if not visualize_chat:  # If visualize chat is empty, initialize it
                    new_visualize_chat = [
                        {
                            "role": "assistant",
                            "content": "📊 **Visualization Mode Activated**\n\nI'm now in visualization mode! I can help you:\n\n• Create charts and graphs from hospital data\n• Analyze patient statistics and trends\n• Generate visual reports and dashboards\n• Visualize medical data patterns\n\nWhat would you like to visualize or analyze?",
                        }
                    ]
                    display_chat = new_visualize_chat
                    stored_visualize_chat = new_visualize_chat
                else:
                    # Return to existing visualize chat with welcome back message for display only
                    display_chat = visualize_chat + [
                        {
                            "role": "assistant",
                            "content": "--- 📊 **Welcome back to Visualization Mode!**\n\n📋 You can see your previous visualization conversation history above, but please note that I'm starting with a fresh conversation context. I don't have access to the details from our previous messages, so feel free to provide any relevant context if you'd like to continue where we left off.\n\nWhat would you like to visualize or analyze today?",
                        }
                    ]
                    stored_visualize_chat = (
                        visualize_chat  # Keep original history without welcome message
                    )

                # Store current chat as original if we're switching from original mode
                if current_mode == "original":
                    original_chat = current_chat

                return (
                    "",
                    display_chat,
                    original_chat,
                    stored_visualize_chat,
                    "visualize",
                )
            # For any other tools (shouldn't happen with current setup)
            return "", current_chat, original_chat, visualize_chat, current_mode

        test_dropdown.change(
            fn=handle_tool_selection,
            inputs=[
                test_dropdown,
                chatbot,
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
            outputs=[
                msg,
                chatbot,
                original_chat_state,
                visualize_chat_state,
                current_mode_state,
            ],
        )  # Load welcome message
        demo.load(
            fn=lambda: [
                {
                    "role": "assistant",
                    "content": "🏥 Welcome to Health AI Hospital Aid (H.A.H.A)! I'm your Medical Assistant powered by advanced AI.\n\n**I can help you with:**\n• Health information and medical guidance\n• Hospital services and patient support\n• Medical consultations and advice\n• Health monitoring and analysis\n• Emergency assistance coordination\n\nFeel free to ask me any health-related questions or concerns!",
                }
            ],
            outputs=chatbot,
        )

    return demo


def handle_ai_response(
    user_message: str,
    model: str,
    temperature: float,
    max_tokens: int,
    specialty: str,
    context: str,
) -> str:
    """
    Handle AI response generation with model routing and LaTeX support

    Args:
        user_message: User's input message
        model: Selected model name
        temperature: Temperature setting
        max_tokens: Maximum tokens
        specialty: Medical specialty
        context: Medical context

    Returns:
        AI response string with LaTeX formatting
    """
    # Medical disclaimer
    disclaimer = "\n\n⚠️ **Medical Disclaimer**: This is for informational purposes only and should not replace professional medical advice. Please consult with a healthcare provider for medical concerns."

    # First, check if this is a database query
    try:
        from ..services.advanced_database_mcp import advanced_database_mcp

        if advanced_database_mcp.is_database_query(user_message):
            # Process database query to get raw data
            db_response = advanced_database_mcp.process_advanced_query(user_message)

            # If we got real data from the database, pass it through AI for analysis
            if (
                "Error processing" not in db_response
                and "Use more specific queries" not in db_response
            ):
                # Create enhanced prompt combining user question with database data
                enhanced_prompt = f"""
User Question: {user_message}

Database Results: 
{db_response}

IMPORTANT: The user specifically requested details/information. Please provide:

1. FIRST: Present the complete data the user requested in a well-formatted, easy-to-read manner
   - Include ALL patient details in a structured format
   - Use proper formatting with line breaks, headers, and organization
   - Format medical values with LaTeX (ages, blood pressure, dosages, etc.)

2. SECOND: After presenting the complete data, provide your professional medical analysis including:
   - Key insights and patterns
   - Medical observations and recommendations
   - Data quality issues or notable findings

Make sure the user gets both the complete information they requested AND your professional analysis.
"""

                # Continue to AI processing with enhanced prompt
                user_message = enhanced_prompt
                context = f"Database query results included in the analysis"

    except Exception as e:
        # If advanced database integration fails, continue with regular AI response
        pass

    if model == "nebius-llama-3.3-70b":
        # Try to use Nebius model first
        try:
            from ..models.nebius_model import NebiusModel

            nebius_model = NebiusModel()

            if nebius_model.is_available():
                # Use higher token limit for database analysis if needed
                analysis_max_tokens = max_tokens
                if "Database Results:" in user_message:
                    analysis_max_tokens = max(
                        max_tokens, 2000
                    )  # Ensure enough space for complete data + analysis

                # Inject hospital schema context for better understanding
                enhanced_context = context if context.strip() else ""

                # Add hospital schema context if this isn't already a database query
                if "Database Results:" not in user_message:
                    try:
                        from ..utils.schema_loader import hospital_schema_loader

                        # Get medical context for general queries
                        medical_context = hospital_schema_loader.get_medical_context()

                        if enhanced_context:
                            enhanced_context = (
                                f"{enhanced_context}\n\n{medical_context}"
                            )
                        else:
                            enhanced_context = medical_context

                    except ImportError:
                        pass  # Continue without hospital context if loader unavailable

                response = nebius_model.generate_response(
                    prompt=user_message,
                    context=enhanced_context if enhanced_context.strip() else None,
                    specialty=specialty,
                    max_tokens=analysis_max_tokens,
                    temperature=temperature,
                    stream=False,
                )
                # Apply LaTeX formatting to the response
                formatted_response = format_medical_response(response, specialty)
                return formatted_response + disclaimer
            else:
                return (
                    "❌ Nebius API is not available. Please check your API key configuration."
                    + disclaimer
                )

        except Exception as e:
            return f"❌ Error using Nebius model: {str(e)}" + disclaimer

    # Fallback responses for other models
    import random

    medical_responses = [
        f"Based on your {specialty.lower()} inquiry about '{user_message}', I need to provide information carefully.",
        f"In {specialty}, regarding '{user_message}', here's what I can share based on general medical knowledge.",
        f"For your {specialty.lower()} question about '{user_message}', let me provide some general guidance.",
        f"Considering the {specialty.lower()} context and your question '{user_message}', here's some information.",
    ]

    if context.strip():
        medical_responses.append(
            f"Given the medical context you provided and your {specialty.lower()} question about '{user_message}', here's what I can tell you."
        )

    base_response = random.choice(medical_responses)

    # Add some medical content based on specialty
    if "pain" in user_message.lower() or "hurt" in user_message.lower():
        base_response += f"\n\nPain can have various causes and should be evaluated by a {specialty.lower()} specialist if persistent."
    elif "fever" in user_message.lower():
        base_response += "\n\nFever is often a sign that your body is fighting an infection. Monitor your temperature and seek medical attention if it's high or persistent."
    elif "medication" in user_message.lower() or "drug" in user_message.lower():
        base_response += "\n\nMedication questions should always be discussed with your healthcare provider or pharmacist who has access to your complete medical history."

    # Apply LaTeX formatting to fallback response
    formatted_base_response = format_medical_response(base_response, specialty)

    return (
        formatted_base_response
        + f"\n\n*Using {model} | Specialty: {specialty} | Temperature: {temperature}*"
        + disclaimer
    )


def get_available_models():
    """Get list of available models"""
    return [
        "nebius-llama-3.3-70b",  # Nebius Studio model (primary)
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-3-sonnet",
        "llama-2-7b",
        "mistral-7b",
    ]


def load_latex_scripts():
    """Load LaTeX rendering scripts and embedded dashboard functionality"""
    return """
    <script src="static/js/latex-renderer.js"></script>
    <script src="static/js/app.js"></script>
    
    <script>
    class HospitalDashboard {
        constructor() {
            this.updateInterval = 30000; // 30 seconds
            this.metrics = {};
            this.currentSection = 'dashboard'; // Track current section
            this.init();
        }

        init() {
            // Wait for page to load
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        }

        setup() {
            this.setupEventListeners();
            this.initializeCharts();
            this.startDataUpdates();
            this.setupNavigation();
            this.createSectionContainers();
            this.initializeInteractiveChart();
            this.showWelcomeMessage();
        }

        createSectionContainers() {
            setTimeout(() => {
                const analysisSection = document.querySelector('.analysis-section');
                const mainContentArea = document.querySelector('.main-content-area');
                
                if (analysisSection) {
                    analysisSection.style.display = 'block';
                    analysisSection.style.opacity = '1';
                }
                
                if (mainContentArea) {
                    mainContentArea.style.display = 'block';
                    mainContentArea.style.opacity = '1';
                }
                
                this.switchToSection('dashboard');
                console.log('Section containers initialized');
            }, 100);
        }

        initializeInteractiveChart() {
            setTimeout(() => {
                this.updateChart('line');
                
                const chartButtons = document.querySelectorAll('.chart-btn');
                chartButtons.forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.handleChartTypeChange(e);
                    });
                });
                
                console.log('Interactive chart initialized with', chartButtons.length, 'buttons');
            }, 1000);
        }

        setupEventListeners() {
            const observer = new MutationObserver(() => {
                const navBtns = document.querySelectorAll('.nav-btn');
                navBtns.forEach(btn => {
                    if (!btn.hasAttribute('data-listener')) {
                        btn.addEventListener('click', (e) => this.handleNavigation(e));
                        btn.setAttribute('data-listener', 'true');
                    }
                });

                const chartBtns = document.querySelectorAll('.chart-btn');
                chartBtns.forEach(btn => {
                    if (!btn.hasAttribute('data-listener')) {
                        btn.addEventListener('click', (e) => this.handleChartTypeChange(e));
                        btn.setAttribute('data-listener', 'true');
                    }
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });
        }

        setupNavigation() {
            setTimeout(() => {
                const navBtns = document.querySelectorAll('.nav-btn');
                console.log('Setting up navigation, found buttons:', navBtns.length);
                
                const hasActiveBtn = Array.from(navBtns).some(btn => btn.classList.contains('active'));
                if (navBtns.length > 0 && !hasActiveBtn) {
                    navBtns[0].classList.add('active');
                    console.log('Set first button as active');
                }
                
                this.switchToSection('dashboard');
            }, 500);
        }

        handleNavigation(event) {
            const clickedBtn = event.target;
            const section = clickedBtn.getAttribute('data-section') || clickedBtn.textContent.toLowerCase();

            // Update active state
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            clickedBtn.classList.add('active');

            // Switch to the selected section
            this.switchToSection(section);
            
            // Show notification
            this.showNotification(`📊 Switched to ${clickedBtn.textContent} section`, 'info');
        }

        switchToSection(section) {
            console.log('Switching to section:', section);
            
            this.currentSection = section;
            
            // Get the new separate sections
            const dashboardSection = document.querySelector('#dashboard-section');
            const dataSection = document.querySelector('#data-section');
            
            // Apply transition effect
            if (dashboardSection) dashboardSection.style.opacity = '0.7';
            if (dataSection) dataSection.style.opacity = '0.7';
            
            setTimeout(() => {
                if (section === 'dashboard') {
                    // Show dashboard section, hide data section
                    if (dashboardSection) {
                        dashboardSection.style.display = 'block';
                        dashboardSection.style.opacity = '1';
                    }
                    if (dataSection) {
                        dataSection.style.display = 'none';
                    }
                    console.log('Dashboard section activated');
                } else if (section === 'data') {
                    // Show data section, hide dashboard section
                    if (dashboardSection) {
                        dashboardSection.style.display = 'none';
                    }
                    if (dataSection) {
                        dataSection.style.display = 'block';
                        dataSection.style.opacity = '1';
                    }
                    console.log('Data section activated');
                    
                    // Initialize data tabs functionality
                    this.initializeDataTabs();
                } else {
                    // Hide both sections for other potential sections
                    if (dashboardSection) dashboardSection.style.display = 'none';
                    if (dataSection) dataSection.style.display = 'none';
                }
            }, 200);
            
            this.loadSectionData(section);
        }

        initializeDataTabs() {
            // Set up data tab switching functionality
            const dataTabs = document.querySelectorAll('.data-tab');
            const dataTableSections = document.querySelectorAll('.data-table-section');
            
            dataTabs.forEach(tab => {
                if (!tab.hasAttribute('data-tab-listener')) {
                    tab.addEventListener('click', (e) => {
                        const targetTab = e.target.getAttribute('data-tab');
                        
                        // Update active tab
                        dataTabs.forEach(t => t.classList.remove('active'));
                        e.target.classList.add('active');
                        
                        // Show corresponding data section
                        dataTableSections.forEach(section => {
                            const sectionId = section.id.replace('-data', '');
                            if (sectionId === targetTab) {
                                section.style.display = 'block';
                                section.classList.add('active');
                            } else {
                                section.style.display = 'none';
                                section.classList.remove('active');
                            }
                        });
                        
                        console.log(`Switched to ${targetTab} data tab`);
                        this.showNotification(`📋 Viewing ${targetTab} data`, 'info');
                    });
                    tab.setAttribute('data-tab-listener', 'true');
                }
            });
        }

        loadSectionData(section) {
            console.log(`Loading ${section} section with simulated data...`);
            
            switch(section) {
                case 'dashboard':
                    this.loadDashboardData();
                    this.updateChartForSection('dashboard');
                    this.showNotification('📊 Dashboard refreshed', 'success');
                    break;
                case 'data':
                    this.loadDataContent();
                    this.showNotification('📋 Data section loaded', 'info');
                    break;
                default:
                    this.loadDashboardData();
                    this.updateChartForSection('dashboard');
                    this.showNotification('📊 Dashboard refreshed', 'success');
                    break;
            }
        }

        loadDataContent() {
            console.log('Loading data content...');
            // Initialize data section - no charts needed
            // This method can be expanded to fetch real data from the backend
            this.showNotification('📊 Data tables ready', 'success');
        }

        updateChartForSection(section) {
            let sectionData;
            
            switch(section) {
                case 'dashboard':
                    sectionData = [
                        { month: 'Jan', patients: 65, revenue: 45, satisfaction: 50 },
                        { month: 'Feb', patients: 58, revenue: 52, satisfaction: 45 },
                        { month: 'Mar', patients: 52, revenue: 58, satisfaction: 40 },
                        { month: 'Apr', patients: 45, revenue: 62, satisfaction: 35 },
                        { month: 'May', patients: 38, revenue: 68, satisfaction: 30 },
                        { month: 'Jun', patients: 45, revenue: 55, satisfaction: 25 },
                        { month: 'Jul', patients: 35, revenue: 48, satisfaction: 20 }
                    ];
                    this.updateLegendForSection(['Patient Count', 'Revenue Data', 'Satisfaction']);
                    break;
                case 'data':
                    sectionData = [
                        { month: 'Jan', admissions: 120, avgStay: 4.2, revenue: 280 },
                        { month: 'Feb', admissions: 135, avgStay: 3.8, revenue: 310 },
                        { month: 'Mar', admissions: 115, avgStay: 4.5, revenue: 265 },
                        { month: 'Apr', admissions: 142, avgStay: 3.9, revenue: 325 },
                        { month: 'May', admissions: 128, avgStay: 4.1, revenue: 295 },
                        { month: 'Jun', admissions: 138, avgStay: 3.7, revenue: 315 },
                        { month: 'Jul', admissions: 125, avgStay: 4.3, revenue: 285 }
                    ];
                    this.updateLegendForSection(['Admissions', 'Avg Stay (days)', 'Revenue ($K)']);
                    break;
                default:
                    return;
            }
            
            if (this.setChartData) {
                this.setChartData(sectionData);
            }
        }

        updateLegendForSection(labels) {
            const legendContainer = document.querySelector('.chart-legend');
            if (!legendContainer || !labels) return;

            const colors = ['#3b82f6', '#22d3ee', '#10b981'];
            
            const legendHTML = labels.map((label, i) => `
                <span class="legend-item">
                    <span class="legend-color" style="background: ${colors[i % colors.length]};"></span>
                    ${label}
                </span>
            `).join('');
            
            legendContainer.innerHTML = legendHTML;
        }

        loadDashboardData() {
            console.log('Loading dashboard data...');
            this.simulateDataUpdate();
        }

        loadDataAnalyticsData() {
            console.log('Loading data analytics...');
            this.refreshAllMetrics();
        }

        handleChartTypeChange(event) {
            console.log('handleChartTypeChange called', event);
            const clickedBtn = event.target;
            const chartType = clickedBtn.getAttribute('data-chart') || clickedBtn.textContent.toLowerCase();
            
            console.log('Chart type detected:', chartType, 'from button:', clickedBtn.textContent);
            
            document.querySelectorAll('.chart-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            clickedBtn.classList.add('active');
            
            this.showNotification(`📊 Switched to ${clickedBtn.textContent} view`, 'info');
            this.updateChart(chartType);
            
            console.log(`Chart type changed to: ${chartType}`);
        }

        updateChart(chartType, data = null) {
            console.log('updateChart called with type:', chartType);
            const chartContainer = document.querySelector('.line-chart');
            if (!chartContainer) {
                console.error('Chart container not found!');
                return;
            }

            console.log('Chart container found, updating to', chartType);

            const chartData = data || this.getChartData();
            console.log('Using chart data:', chartData);

            chartContainer.style.opacity = '0.3';
            chartContainer.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                switch(chartType) {
                    case 'line':
                        console.log('Generating dynamic line chart');
                        chartContainer.innerHTML = this.generateDynamicLineChart(chartData);
                        break;
                    case 'bar':
                        console.log('Generating dynamic bar chart');
                        chartContainer.innerHTML = this.generateDynamicBarChart(chartData);
                        break;
                    case 'pie':
                        console.log('Generating dynamic pie chart');
                        chartContainer.innerHTML = this.generateDynamicPieChart(chartData);
                        break;
                    case 'scatter':
                        console.log('Generating dynamic scatter chart');
                        chartContainer.innerHTML = this.generateDynamicScatterChart(chartData);
                        break;
                    default:
                        console.log('Default: generating dynamic line chart');
                        chartContainer.innerHTML = this.generateDynamicLineChart(chartData);
                }
                
                this.updateDynamicLegend(chartData, chartType);
                
                chartContainer.style.opacity = '1';
                chartContainer.style.transform = 'scale(1)';
                console.log('Chart updated successfully to', chartType);
            }, 150);
        }

        getCurrentChartData() {
            return [
                { month: 'Jan', patients: 65, revenue: 45, satisfaction: 50 },
                { month: 'Feb', patients: 58, revenue: 52, satisfaction: 45 },
                { month: 'Mar', patients: 52, revenue: 58, satisfaction: 40 },
                { month: 'Apr', patients: 45, revenue: 62, satisfaction: 35 },
                { month: 'May', patients: 38, revenue: 68, satisfaction: 30 },
                { month: 'Jun', patients: 45, revenue: 55, satisfaction: 25 },
                { month: 'Jul', patients: 35, revenue: 48, satisfaction: 20 }
            ];
        }

        analyzeDataStructure(data) {
            if (!data || data.length === 0) return { xField: null, yFields: [], colors: [] };
            
            const firstItem = data[0];
            const fields = Object.keys(firstItem);
            
            const xField = fields.find(field => 
                typeof firstItem[field] === 'string' || 
                field.toLowerCase().includes('time') ||
                field.toLowerCase().includes('date') ||
                field.toLowerCase().includes('month') ||
                field.toLowerCase().includes('category') ||
                field.toLowerCase().includes('label')
            ) || fields[0];
            
            const yFields = fields.filter(field => 
                field !== xField && 
                typeof firstItem[field] === 'number'
            );
            
            const colorPalette = [
                '#3b82f6', '#22d3ee', '#10b981', '#f59e0b', 
                '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', 
                '#f97316', '#ec4899', '#6366f1', '#14b8a6'
            ];
            
            const colors = yFields.map((field, index) => 
                colorPalette[index % colorPalette.length]
            );
            
            return { xField, yFields, colors };
        }

        generateDynamicLineChart(data) {
            const { xField, yFields, colors } = this.analyzeDataStructure(data);
            console.log('Line chart structure:', { xField, yFields, colors });
            
            if (!xField || yFields.length === 0) {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid data structure for line chart</div>';
            }

            const allValues = data.flatMap(d => yFields.map(field => d[field] || 0));
            const minValue = Math.min(...allValues);
            const maxValue = Math.max(...allValues);
            const valueRange = maxValue - minValue || 1;
            
            const scaleY = (value) => 250 - ((value - minValue) / valueRange) * 180;
            const scaleX = (index) => 80 + index * (440 / (data.length - 1));

            return `
                <svg width="100%" height="400" viewBox="0 0 600 300">
                    <defs>
                        <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                            <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    
                    ${Array.from({length: 6}, (_, i) => {
                        const value = Math.round(maxValue - (i * valueRange / 5));
                        const y = 50 + i * 40;
                        return `<text x="30" y="${y}" fill="#64748b" font-size="12" text-anchor="end">${value}</text>`;
                    }).join('')}
                    
                    ${data.map((d, i) => `<text x="${scaleX(i)}" y="280" fill="#64748b" font-size="12" text-anchor="middle">${d[xField]}</text>`).join('')}
                    
                    ${yFields.map((field, fieldIndex) => {
                        const lineColor = colors[fieldIndex];
                        const pathData = data.map((d, i) => `${scaleX(i)} ${scaleY(d[field] || 0)}`).join(' L ');
                        return `
                            <path d="M ${pathData}" 
                                  stroke="${lineColor}" stroke-width="3" fill="none" stroke-linecap="round"/>
                            
                            ${data.map((d, i) => `<circle cx="${scaleX(i)}" cy="${scaleY(d[field] || 0)}" r="4" fill="${lineColor}"/>`).join('')}
                        `;
                    }).join('')}
                </svg>
            `;
        }

        generateDynamicBarChart(data) {
            const { xField, yFields, colors } = this.analyzeDataStructure(data);
            
            if (!xField || yFields.length === 0) {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid data structure for bar chart</div>';
            }

            const allValues = data.flatMap(d => yFields.map(field => d[field] || 0));
            const minValue = Math.max(0, Math.min(...allValues));
            const maxValue = Math.max(...allValues);
            const valueRange = maxValue - minValue || 1;
            
            const scaleY = (value) => 250 - ((value - minValue) / valueRange) * 180;
            const scaleHeight = (value) => ((value - minValue) / valueRange) * 180;
            const categoryWidth = 440 / data.length;
            const barWidth = Math.min(15, (categoryWidth - 10) / yFields.length);

            return `
                <svg width="100%" height="400" viewBox="0 0 600 300">
                    <defs>
                        <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                            <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    
                    ${Array.from({length: 6}, (_, i) => {
                        const value = Math.round(maxValue - (i * valueRange / 5));
                        const y = 50 + i * 40;
                        return `<text x="30" y="${y}" fill="#64748b" font-size="12" text-anchor="end">${value}</text>`;
                    }).join('')}
                    
                    ${data.map((d, i) => {
                        const centerX = 80 + i * categoryWidth + categoryWidth / 2;
                        return `<text x="${centerX}" y="280" fill="#64748b" font-size="12" text-anchor="middle">${d[xField]}</text>`;
                    }).join('')}
                    
                    ${data.map((d, dataIndex) => {
                        const baseX = 80 + dataIndex * categoryWidth;
                        const startX = baseX + (categoryWidth - (yFields.length * barWidth + (yFields.length - 1) * 2)) / 2;
                        
                        return yFields.map((field, fieldIndex) => {
                            const barColor = colors[fieldIndex];
                            const value = d[field] || 0;
                            const barHeight = scaleHeight(value);
                            const barY = scaleY(value);
                            const barX = startX + fieldIndex * (barWidth + 2);
                            
                            return `
                                <rect x="${barX}" y="${barY}" width="${barWidth}" height="${barHeight}" 
                                      fill="${barColor}" rx="2" opacity="0.9"/>
                                <text x="${barX + barWidth/2}" y="${barY - 5}" fill="#64748b" 
                                      font-size="10" text-anchor="middle">${value}</text>
                            `;
                        }).join('');
                    }).join('')}
                </svg>
            `;
        }

        generateDynamicPieChart(data) {
            console.log('Generating dynamic pie chart with data:', data);
            
            if (!data || data.length === 0) {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">No data available for pie chart</div>';
            }

            const { xField, yFields, colors } = this.analyzeDataStructure(data);
            
            let pieData = [];
            
            if (data[0].hasOwnProperty('value') && data[0].hasOwnProperty('label')) {
                pieData = data.map((d, i) => ({
                    label: d.label,
                    value: d.value,
                    color: d.color || colors[i % colors.length]
                }));
            } else if (yFields.length === 1) {
                pieData = data.map((d, i) => ({
                    label: d[xField] || `Item ${i + 1}`,
                    value: d[yFields[0]] || 0,
                    color: colors[i % colors.length]
                }));
            } else if (yFields.length > 1) {
                pieData = yFields.map((field, i) => ({
                    label: field.charAt(0).toUpperCase() + field.slice(1),
                    value: data.reduce((sum, d) => sum + (d[field] || 0), 0),
                    color: colors[i % colors.length]
                }));
            } else {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid numeric data for pie chart</div>';
            }

            const total = pieData.reduce((sum, d) => sum + d.value, 0);
            if (total === 0) {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">All values are zero</div>';
            }

            let currentAngle = 0;
            const radius = 80;
            const centerX = 300;
            const centerY = 130;

            const slices = pieData.map(d => {
                const startAngle = currentAngle;
                const endAngle = currentAngle + (d.value / total) * 2 * Math.PI;
                currentAngle = endAngle;

                const x1 = centerX + radius * Math.cos(startAngle);
                const y1 = centerY + radius * Math.sin(startAngle);
                const x2 = centerX + radius * Math.cos(endAngle);
                const y2 = centerY + radius * Math.sin(endAngle);

                const largeArcFlag = endAngle - startAngle <= Math.PI ? "0" : "1";
                const percentage = Math.round((d.value / total) * 100);

                return {
                    ...d,
                    percentage,
                    path: `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`,
                    labelX: centerX + (radius * 0.7) * Math.cos((startAngle + endAngle) / 2),
                    labelY: centerY + (radius * 0.7) * Math.sin((startAngle + endAngle) / 2)
                };
            });

            return `
                <svg width="100%" height="400" viewBox="0 0 600 300">
                    ${slices.map(slice => `
                        <path d="${slice.path}" fill="${slice.color}" stroke="white" stroke-width="2"/>
                        ${slice.percentage > 5 ? `<text x="${slice.labelX}" y="${slice.labelY}" fill="white" font-size="12" text-anchor="middle" font-weight="600">${slice.percentage}%</text>` : ''}
                    `).join('')}
                    
                    ${pieData.map((d, i) => `
                        <rect x="450" y="${50 + i * 20}" width="12" height="12" fill="${d.color}" rx="2"/>
                        <text x="470" y="${60 + i * 20}" fill="#64748b" font-size="11">${d.label} (${Math.round((d.value / total) * 100)}%)</text>
                    `).join('')}
                    
                    <text x="300" y="30" fill="#1e293b" font-size="16" text-anchor="middle" font-weight="600">Data Distribution</text>
                </svg>
            `;
        }

        generateDynamicScatterChart(data) {
            console.log('Generating dynamic scatter chart with data:', data);
            
            if (!data || data.length === 0) {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">No data available for scatter chart</div>';
            }

            const { xField, yFields, colors } = this.analyzeDataStructure(data);
            
            if (yFields.length < 2) {
                return '<div style="padding: 20px; text-align: center; color: #64748b;">Scatter chart requires at least 2 numeric fields</div>';
            }

            const xAxisField = yFields[0];
            const yAxisField = yFields[1];
            const sizeField = yFields[2] || null;
            const labelField = xField;
            
            const xValues = data.map(d => d[xAxisField] || 0);
            const yValues = data.map(d => d[yAxisField] || 0);
            const sizeValues = sizeField ? data.map(d => d[sizeField] || 0) : [];
            
            const xMin = Math.min(...xValues);
            const xMax = Math.max(...xValues);
            const yMin = Math.min(...yValues);
            const yMax = Math.max(...yValues);
            const sizeMin = sizeValues.length ? Math.min(...sizeValues) : 5;
            const sizeMax = sizeValues.length ? Math.max(...sizeValues) : 10;
            
            const xRange = xMax - xMin || 1;
            const yRange = yMax - yMin || 1;
            const sizeRange = sizeMax - sizeMin || 1;
            
            const scaleX = (value) => 50 + ((value - xMin) / xRange) * 500;
            const scaleY = (value) => 250 - ((value - yMin) / yRange) * 200;
            const scaleSize = (value) => sizeField ? 
                5 + ((value - sizeMin) / sizeRange) * 10 : 
                8;

            return `
                <svg width="100%" height="400" viewBox="0 0 600 300">
                    <defs>
                        <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                            <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    
                    <line x1="50" y1="250" x2="550" y2="250" stroke="#e2e8f0" stroke-width="2"/>
                    <text x="300" y="290" fill="#64748b" font-size="12" text-anchor="middle">${xAxisField.charAt(0).toUpperCase() + xAxisField.slice(1)}</text>
                    
                    <line x1="50" y1="50" x2="50" y2="250" stroke="#e2e8f0" stroke-width="2"/>
                    <text x="25" y="150" fill="#64748b" font-size="12" text-anchor="middle" transform="rotate(-90 25 150)">${yAxisField.charAt(0).toUpperCase() + yAxisField.slice(1)}</text>
                    
                    ${Array.from({length: 6}, (_, i) => {
                        const value = Math.round(xMin + (i * xRange / 5));
                        const x = 50 + i * 100;
                        return `<text x="${x}" y="265" fill="#64748b" font-size="10" text-anchor="middle">${value}</text>`;
                    }).join('')}
                    
                    ${Array.from({length: 6}, (_, i) => {
                        const value = Math.round(yMax - (i * yRange / 5));
                        const y = 50 + i * 40;
                        return `<text x="35" y="${y}" fill="#64748b" font-size="10" text-anchor="end">${value}</text>`;
                    }).join('')}
                    
                    ${data.map((d, i) => {
                        const x = scaleX(d[xAxisField] || 0);
                        const y = scaleY(d[yAxisField] || 0);
                        const size = scaleSize(sizeField ? (d[sizeField] || 0) : 8);
                        const color = colors[i % colors.length];
                        const label = d[labelField] || `Point ${i + 1}`;
                        
                        return `
                            <circle cx="${x}" cy="${y}" r="${size}" 
                                    fill="${color}" opacity="0.7" 
                                    stroke="${color}" stroke-width="2"/>
                            <text x="${x}" y="${y - size - 5}" 
                                  fill="#64748b" font-size="10" text-anchor="middle">${label}</text>
                        `;
                    }).join('')}
                    
                    <text x="300" y="30" fill="#1e293b" font-size="16" text-anchor="middle" font-weight="600">${yAxisField.charAt(0).toUpperCase() + yAxisField.slice(1)} vs ${xAxisField.charAt(0).toUpperCase() + xAxisField.slice(1)}</text>
                </svg>
            `;
        }

        updateDynamicLegend(data, chartType) {
            const legendContainer = document.querySelector('.chart-legend');
            if (!legendContainer) return;

            const { xField, yFields, colors } = this.analyzeDataStructure(data);
            
            let legendHTML = '';
            
            if (chartType === 'pie') {
                if (data[0]?.hasOwnProperty('value') && data[0]?.hasOwnProperty('label')) {
                    legendHTML = data.map((d, i) => `
                        <span class="legend-item">
                            <span class="legend-color" style="background: ${d.color || colors[i % colors.length]};"></span>
                            ${d.label}
                        </span>
                    `).join('');
                } else {
                    legendHTML = yFields.map((field, i) => `
                        <span class="legend-item">
                            <span class="legend-color" style="background: ${colors[i]};"></span>
                            ${field.charAt(0).toUpperCase() + field.slice(1)}
                        </span>
                    `).join('');
                }
            } else if (chartType === 'scatter') {
                if (yFields.length >= 2) {
                    legendHTML = `
                        <span class="legend-item">
                            <span class="legend-color" style="background: ${colors[0]};"></span>
                            X: ${yFields[0].charAt(0).toUpperCase() + yFields[0].slice(1)}
                        </span>
                        <span class="legend-item">
                            <span class="legend-color" style="background: ${colors[1]};"></span>
                            Y: ${yFields[1].charAt(0).toUpperCase() + yFields[1].slice(1)}
                        </span>
                    `;
                }
            } else {
                legendHTML = yFields.map((field, i) => `
                    <span class="legend-item">
                        <span class="legend-color" style="background: ${colors[i]};"></span>
                        ${field.charAt(0).toUpperCase() + field.slice(1)}
                    </span>
                `).join('');
            }
            
            legendContainer.innerHTML = legendHTML;
        }

        // Initialize and update methods
        initializeCharts() {
            this.initICUOccupancyChart();
            this.initEmergencyLoadChart();
            this.initStaffAvailability();
            this.initToolUsageChart();
        }

        initEmergencyLoadChart() {
            const loadPath = document.querySelector('.load-path');
            if (loadPath) {
                this.metrics.emergencyLoad = {
                    element: loadPath,
                    data: [70, 50, 45, 40, 35, 30, 25],
                    animate: (newData) => {
                        const path = this.generateLoadPath(newData);
                        loadPath.setAttribute('d', path);
                    }
                };
            }
        }

        initICUOccupancyChart() {
            const circle = document.querySelector('.progress-circle-fill');
            const text = document.querySelector('.progress-text');
            
            if (circle && text) {
                this.metrics.icuOccupancy = {
                    element: circle,
                    textElement: text,
                    value: 71,
                    animate: (newValue) => {
                        const circumference = 2 * Math.PI * 54;
                        const offset = circumference - (newValue / 100) * circumference;
                        circle.style.strokeDashoffset = offset + 'px';
                        text.textContent = newValue + '%';
                    }
                };
            }
        }

        initStaffAvailability() {
            const doctorsProgress = document.querySelector('.doctors-progress');
            const nursesProgress = document.querySelector('.nurses-progress');
            
            if (doctorsProgress && nursesProgress) {
                this.metrics.staffAvailability = {
                    doctors: { element: doctorsProgress, value: 75 },
                    nurses: { element: nursesProgress, value: 60 },
                    animate: (doctorValue, nurseValue) => {
                        doctorsProgress.style.width = doctorValue + '%';
                        nursesProgress.style.width = nurseValue + '%';
                        
                        const doctorPercentage = document.querySelector('.staff-item:first-child .staff-percentage');
                        const nursePercentage = document.querySelector('.staff-item:last-child .staff-percentage');
                        if (doctorPercentage) doctorPercentage.textContent = doctorValue + '%';
                        if (nursePercentage) nursePercentage.textContent = nurseValue + '%';
                    }
                };
            }
        }

        initToolUsageChart() {
            const bars = document.querySelectorAll('.usage-chart .bar');
            if (bars.length > 0) {
                this.metrics.toolUsage = {
                    elements: Array.from(bars),
                    values: [60, 40, 70, 35, 85],
                    animate: (newValues) => {
                        bars.forEach((bar, index) => {
                            if (newValues[index] !== undefined) {
                                bar.style.height = newValues[index] + '%';
                            }
                        });
                    }
                };
            }
        }

        startDataUpdates() {
            this.updateDashboardData();
            setInterval(() => {
                this.updateDashboardData();
            }, this.updateInterval);
        }

        updateDashboardData() {
            console.log('Updating dashboard with simulated real-time data...');
            this.simulateDataUpdate();
        }

        simulateDataUpdate() {
            const currentICU = this.metrics.icuOccupancy?.value || 71;
            const newICU = Math.max(50, Math.min(95, currentICU + (Math.random() - 0.5) * 10));
            this.updateICUOccupancy(Math.round(newICU));

            const currentDoctors = this.metrics.staffAvailability?.doctors.value || 75;
            const currentNurses = this.metrics.staffAvailability?.nurses.value || 60;
            const newDoctors = Math.max(40, Math.min(90, currentDoctors + (Math.random() - 0.5) * 15));
            const newNurses = Math.max(30, Math.min(85, currentNurses + (Math.random() - 0.5) * 20));
            this.updateStaffAvailability(Math.round(newDoctors), Math.round(newNurses));

            const newToolUsage = this.metrics.toolUsage?.values.map(val => 
                Math.max(20, Math.min(90, val + (Math.random() - 0.5) * 20))
            ) || [60, 40, 70, 35, 85];
            this.updateToolUsage(newToolUsage.map(val => Math.round(val)));

            const newEmergencyData = Array.from({length: 7}, () => 
                Math.max(20, Math.min(80, 50 + (Math.random() - 0.5) * 40))
            );
            this.updateEmergencyLoad(newEmergencyData);
        }

        updateICUOccupancy(value) {
            if (this.metrics.icuOccupancy) {
                this.metrics.icuOccupancy.value = value;
                this.metrics.icuOccupancy.animate(value);
            }
        }

        updateStaffAvailability(doctorValue, nurseValue) {
            if (this.metrics.staffAvailability) {
                this.metrics.staffAvailability.doctors.value = doctorValue;
                this.metrics.staffAvailability.nurses.value = nurseValue;
                this.metrics.staffAvailability.animate(doctorValue, nurseValue);
            }
        }

        updateToolUsage(values) {
            if (this.metrics.toolUsage) {
                this.metrics.toolUsage.values = values;
                this.metrics.toolUsage.animate(values);
            }
        }

        updateEmergencyLoad(data) {
            if (this.metrics.emergencyLoad) {
                this.metrics.emergencyLoad.data = data;
                this.metrics.emergencyLoad.animate(data);
            }
        }

        generateLoadPath(data) {
            const points = data.map((value, index) => {
                const x = 10 + (index * 30);
                const y = 70 - (value * 0.8);
                return `${x} ${y}`;
            });
            
            return `M ${points[0]} Q ${points[1]} T ${points.slice(2).join(' T ')}`;
        }

        refreshAllMetrics() {
            this.simulateDataUpdate();
            this.showNotification('Dashboard updated successfully', 'success');
        }

        showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = 'dashboard-notification';
            notification.textContent = message;
            
            if (type === 'success') {
                notification.style.background = '#10b981';
            } else if (type === 'error') {
                notification.style.background = '#ef4444';
            } else {
                notification.style.background = '#3b82f6';
            }
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }, 3000);
        }

        showWelcomeMessage() {
            setTimeout(() => {
                this.showNotification('Interactive Dashboard Loaded! 🎉', 'success');
                this.ensureChartInteractivity();
            }, 1000);
        }

        ensureChartInteractivity() {
            console.log('Ensuring chart interactivity...');
            
            const chartContainer = document.querySelector('.line-chart');
            if (chartContainer && !chartContainer.hasAttribute('data-initialized')) {
                console.log('Force initializing chart...');
                this.updateChart('line');
                chartContainer.setAttribute('data-initialized', 'true');
            }
            
            const chartBtns = document.querySelectorAll('.chart-btn');
            console.log('Found chart buttons:', chartBtns.length);
            
            chartBtns.forEach((btn, index) => {
                if (!btn.hasAttribute('data-chart-listener')) {
                    console.log('Adding listener to button', index, btn.textContent);
                    btn.addEventListener('click', (e) => {
                        console.log('Chart button clicked:', e.target.textContent);
                        this.handleChartTypeChange(e);
                    });
                    btn.setAttribute('data-chart-listener', 'true');
                }
            });

            // Initialize analysis selector functionality
            this.initializeAnalysisSelector();
        }

        initializeAnalysisSelector() {
            const analysisSelector = document.querySelector('#analysis-selector');
            
            if (analysisSelector && !analysisSelector.hasAttribute('data-initialized')) {
                console.log('Initializing analysis selector...');
                
                // Set default selection
                analysisSelector.value = 'bed-occupancy';
                
                analysisSelector.addEventListener('change', (e) => {
                    this.handleAnalysisSelection(e.target.value, e.target.selectedOptions[0].text);
                });
                
                analysisSelector.setAttribute('data-initialized', 'true');
                console.log('Analysis selector initialized with default value:', analysisSelector.value);
                
                // Load initial data for default selection
                this.handleAnalysisSelection('bed-occupancy', 'Real-time bed occupancy by ward & ICU');
            }
        }

        handleAnalysisSelection(value, text) {
            console.log('Analysis selection changed to:', value, text);
            
            // Show notification about the selection
            this.showNotification(`📊 Loading ${text} analysis...`, 'info');
            
            // Update chart data based on selection
            let analysisData = this.getAnalysisData(value);
            
            // Update chart legend based on analysis type
            this.updateAnalysisLegend(value);
            
            // Update the chart with new data
            const activeBtn = document.querySelector('.chart-btn.active');
            const chartType = activeBtn ? activeBtn.getAttribute('data-chart') || 'line' : 'line';
            
            this.updateChart(chartType, analysisData);
            
            // Show completion notification
            setTimeout(() => {
                this.showNotification(`✅ ${text} analysis loaded`, 'success');
            }, 800);
        }

        getAnalysisData(analysisType) {
            const dataTemplates = {
                'bed-occupancy': [
                    { department: 'ICU', current: 85, capacity: 100, occupancy: 85 },
                    { department: 'Emergency', current: 42, capacity: 50, occupancy: 84 },
                    { department: 'Surgery', current: 38, capacity: 45, occupancy: 84 },
                    { department: 'Cardiology', current: 28, capacity: 35, occupancy: 80 },
                    { department: 'Pediatrics', current: 22, capacity: 30, occupancy: 73 },
                    { department: 'Maternity', current: 15, capacity: 25, occupancy: 60 },
                    { department: 'Orthopedics', current: 18, capacity: 25, occupancy: 72 }
                ],
                'alos': [
                    { procedure: 'Cardiac Surgery', ward: 'ICU', alos: 5.2, target: 4.5 },
                    { procedure: 'Hip Replacement', ward: 'Orthopedics', alos: 3.8, target: 3.5 },
                    { procedure: 'Appendectomy', ward: 'Surgery', alos: 2.1, target: 2.0 },
                    { procedure: 'Normal Birth', ward: 'Maternity', alos: 1.8, target: 1.5 },
                    { procedure: 'Pneumonia', ward: 'Internal', alos: 4.5, target: 4.0 },
                    { procedure: 'Broken Arm', ward: 'Emergency', alos: 0.8, target: 0.5 },
                    { procedure: 'Stroke', ward: 'Neurology', alos: 7.2, target: 6.5 }
                ],
                'staff-workload': [
                    { shift: 'Night', doctors: 12, nurses: 35, workload: 85, efficiency: 78 },
                    { shift: 'Morning', doctors: 45, nurses: 78, workload: 92, efficiency: 85 },
                    { shift: 'Afternoon', doctors: 38, nurses: 65, workload: 88, efficiency: 82 },
                    { shift: 'Evening', doctors: 22, nurses: 48, workload: 75, efficiency: 80 },
                    { shift: 'Weekend', doctors: 18, nurses: 42, workload: 68, efficiency: 75 },
                    { shift: 'Holiday', doctors: 15, nurses: 38, workload: 65, efficiency: 72 },
                    { shift: 'Emergency', doctors: 8, nurses: 25, workload: 95, efficiency: 88 }
                ],
                'tool-utilisation': [
                    { equipment: 'MRI', utilization: 78, idle: 22, maintenance: 5 },
                    { equipment: 'CT Scanner', utilization: 85, idle: 15, maintenance: 8 },
                    { equipment: 'X-Ray', utilization: 92, idle: 8, maintenance: 3 },
                    { equipment: 'Ultrasound', utilization: 68, idle: 32, maintenance: 6 },
                    { equipment: 'ECG', utilization: 55, idle: 45, maintenance: 2 },
                    { equipment: 'Ventilators', utilization: 72, idle: 28, maintenance: 12 },
                    { equipment: 'Dialysis', utilization: 88, idle: 12, maintenance: 15 }
                ],
                'inventory-expiry': [
                    { category: 'Medications', expiring: 15, total: 250, urgent: 3 },
                    { category: 'Surgical', expiring: 8, total: 120, urgent: 1 },
                    { category: 'Consumables', expiring: 22, total: 450, urgent: 5 },
                    { category: 'Lab Supplies', expiring: 12, total: 180, urgent: 2 },
                    { category: 'Blood Products', expiring: 6, total: 85, urgent: 4 },
                    { category: 'Vaccines', expiring: 4, total: 95, urgent: 1 },
                    { category: 'PPE', expiring: 18, total: 320, urgent: 2 }
                ],
                'bed-census': [
                    { timeframe: '6 Hours', predicted: 245, actual: 238, confidence: 95 },
                    { timeframe: '12 Hours', predicted: 252, actual: 248, confidence: 92 },
                    { timeframe: '24 Hours', predicted: 268, actual: null, confidence: 88 },
                    { timeframe: '48 Hours', predicted: 275, actual: null, confidence: 82 },
                    { timeframe: '72 Hours', predicted: 282, actual: null, confidence: 78 },
                    { timeframe: '1 Week', predicted: 295, actual: null, confidence: 72 },
                    { timeframe: '2 Weeks', predicted: 285, actual: null, confidence: 65 }
                ],
                'elective-emergency': [
                    { category: 'Elective Surgery', count: 125, revenue: 450, satisfaction: 92 },
                    { category: 'Emergency Surgery', count: 78, revenue: 320, satisfaction: 85 },
                    { category: 'Elective Cardio', count: 45, revenue: 380, satisfaction: 94 },
                    { category: 'Emergency Cardio', count: 32, revenue: 280, satisfaction: 88 },
                    { category: 'Elective Ortho', count: 68, revenue: 290, satisfaction: 91 },
                    { category: 'Emergency Ortho', count: 42, revenue: 185, satisfaction: 82 },
                    { category: 'Planned Admission', count: 156, revenue: 220, satisfaction: 89 }
                ],
                'los-prediction': [
                    { patient: 'P001', predicted: 4.2, actual: 3.8, accuracy: 95, condition: 'Pneumonia' },
                    { patient: 'P002', predicted: 6.5, actual: 6.8, accuracy: 92, condition: 'Surgery' },
                    { patient: 'P003', predicted: 2.1, actual: 2.0, accuracy: 98, condition: 'Observation' },
                    { patient: 'P004', predicted: 8.2, actual: null, accuracy: 88, condition: 'Cardiac' },
                    { patient: 'P005', predicted: 3.5, actual: null, accuracy: 90, condition: 'Orthopedic' },
                    { patient: 'P006', predicted: 5.8, actual: null, accuracy: 85, condition: 'Neurological' },
                    { patient: 'P007', predicted: 1.2, actual: null, accuracy: 94, condition: 'Emergency' }
                ]
            };
            
            return dataTemplates[analysisType] || this.getCurrentChartData();
        }

        updateAnalysisLegend(analysisType) {
            const legendMappings = {
                'bed-occupancy': ['Current Occupancy', 'Capacity', 'Occupancy Rate'],
                'alos': ['Average LOS', 'Target LOS', 'Efficiency'],
                'staff-workload': ['Doctor Count', 'Nurse Count', 'Workload %'],
                'tool-utilisation': ['Utilization %', 'Idle Time %', 'Maintenance %'],
                'inventory-expiry': ['Expiring Items', 'Total Items', 'Urgent Items'],
                'bed-census': ['Predicted', 'Actual', 'Confidence %'],
                'elective-emergency': ['Patient Count', 'Revenue ($K)', 'Satisfaction %'],
                'los-prediction': ['Predicted LOS', 'Actual LOS', 'Accuracy %']
            };
            
            const labels = legendMappings[analysisType] || ['Patient Count', 'Revenue Data', 'Satisfaction'];
            this.updateLegendForSection(labels);
        }

        setChartData(newData) {
            console.log('Setting new chart data:', newData);
            this.chartData = newData;
            
            const activeBtn = document.querySelector('.chart-btn.active');
            if (activeBtn) {
                const chartType = activeBtn.getAttribute('data-chart') || 'line';
                this.updateChart(chartType, newData);
            }
        }

        getChartData() {
            return this.chartData || this.getCurrentChartData();
        }
    }

    // Initialize dashboard
    window.hospitalDashboard = new HospitalDashboard();

    // Global function to update chart data
    window.updateChartData = function(newData) {
        if (window.hospitalDashboard) {
            window.hospitalDashboard.setChartData(newData);
            console.log('Chart data updated globally');
        }
    };

    // Direct initialization for chart interactivity
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, setting up chart interactivity immediately...');
        
        setTimeout(() => {
            const chartButtons = document.querySelectorAll('.chart-btn');
            console.log('Direct setup: Found', chartButtons.length, 'chart buttons');
            
            chartButtons.forEach((btn, index) => {
                console.log('Setting up button', index, ':', btn.textContent);
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const chartType = this.getAttribute('data-chart') || this.textContent.toLowerCase();
                    console.log('Direct click handler - Chart type:', chartType);
                    
                    chartButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    if (window.hospitalDashboard) {
                        window.hospitalDashboard.updateChart(chartType);
                        window.hospitalDashboard.showNotification(`📊 Switched to ${this.textContent} view`, 'info');
                    }
                });
            });
            
            // Direct setup for analysis selector
            const analysisSelector = document.querySelector('#analysis-selector');
            if (analysisSelector && !analysisSelector.hasAttribute('data-direct-listener')) {
                console.log('Direct setup: Setting up analysis selector');
                analysisSelector.value = 'bed-occupancy';
                
                analysisSelector.addEventListener('change', function(e) {
                    console.log('Direct analysis selector change:', e.target.value);
                    if (window.hospitalDashboard) {
                        const selectedText = e.target.selectedOptions[0].text;
                        window.hospitalDashboard.handleAnalysisSelection(e.target.value, selectedText);
                    }
                });
                
                analysisSelector.setAttribute('data-direct-listener', 'true');
                console.log('Analysis selector direct setup complete');
            }
            
            if (window.hospitalDashboard) {
                console.log('Direct initialization with line chart');
                window.hospitalDashboard.updateChart('line');
            }
        }, 2000);
    });
    </script>
    """
