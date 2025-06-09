"""
Main Gradio Interface Components - Modern Hospital Dashboard Interface
"""

import asyncio
import time
from typing import Any, Dict, List

import gradio as gr

from ..models.mcp_handler import MCPHandler
from ..models.nebius_model import NebiusModel
from ..utils.helpers import process_user_input
from ..utils.latex_formatter import format_medical_response


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

    with gr.Blocks(
        title="Health AI Hospital Aid (H.A.H.A)",
        css=load_modern_hospital_css(),
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
                """                )                # Chat Interface - Normal Chat
                chatbot = gr.Chatbot(
                    type="messages",
                    height=600,
                    show_copy_button=False,
                    show_share_button=True,
                    container=False,
                    layout="bubble",
                    elem_classes="chatbot-gr-chatbot",
                )# Chat Input Area - Standard
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask about hospital status, patients, or medical queries...",
                        show_label=False,
                        lines=1,
                        max_lines=3,
                        container=False,
                        scale=4,
                    )
                    send_btn = gr.Button("→", size="sm", scale=0, min_width=40)                # Test Section with Dropdown
                with gr.Row(elem_classes="tools-section"):
                    with gr.Column(scale=1):                        test_dropdown = gr.Dropdown(
                            choices=[
                                "Main Chat",
                                "Visualize"
                            ],
                            label="",
                            value="Main Chat",
                            interactive=True,
                            container=True,
                            elem_classes="custom-test-dropdown",
                            show_label=False
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
                    with gr.Column(scale=3):
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

                # Navigation Buttons Row - Updated to match image
                gr.HTML(
                    """
                <div class="nav-buttons-container">
                    <button class="nav-btn active" data-section="dashboard">Dashboard</button>
                    <button class="nav-btn" data-section="alerts">Alerts</button>
                    <button class="nav-btn" data-section="resources">Resources</button>
                    <button class="nav-btn" data-section="data">Data</button>
                </div>
                """
                )

                # Main Content Area - Always Visible Analysis Section
                gr.HTML(
                    """
                <div class="main-content-area">
                    <div class="analysis-section">
                        <h2 class="analysis-title">Analysis Title</h2>
                        
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
                </div>
                """                )

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
                    yield history, ""        # Quick action handler
        def handle_helpline():
            return "", [
                {
                    "role": "user",
                    "content": "Connect me to the hospital helpline for urgent assistance",
                },
                {
                    "role": "assistant",
                    "content": "📞 The helpline number of the hospital is **555-HELP (555-4357)**.\n\nOur helpline is available 24/7 for urgent assistance. Please call immediately if you have any medical emergencies or need immediate support.",                }
            ]

        # Chat state management
        original_chat_state = gr.State([])  # Store original chat history
        visualize_chat_state = gr.State([])  # Store visualize chat history
        current_mode_state = gr.State("original")  # Track current mode: "original" or "visualize"

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
            current_mode
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
                current_mode_state
            ],
            outputs=[chatbot, msg, original_chat_state, visualize_chat_state, current_mode_state],
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
                current_mode_state
            ],
            outputs=[chatbot, msg, original_chat_state, visualize_chat_state, current_mode_state],
            show_progress="hidden",
        )        # Update helpline handler to work with state management
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
                }
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
                
            return "", new_chat_display, new_original_chat, new_visualize_chat, current_mode

        helpline_btn.click(
            fn=handle_helpline_with_state,
            inputs=[original_chat_state, visualize_chat_state, current_mode_state],
            outputs=[msg, chatbot, original_chat_state, visualize_chat_state, current_mode_state],        )

        # Test dropdown handler
        def handle_tool_selection(tool_name, current_chat, original_chat, visualize_chat, current_mode):
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
                            "content": "--- 🔄 **Welcome back to the main chat!**\n\n📋 You can see your previous conversation history above, but please note that I'm starting with a fresh conversation context. I don't have access to the details from our previous messages, so feel free to provide any relevant context if you'd like to continue where we left off.\n\nHow can I assist you today?"
                        }
                    ]
                    stored_original_chat = original_chat  # Keep original history without welcome message
                else:
                    display_chat = original_chat
                    stored_original_chat = original_chat
                return "", display_chat, stored_original_chat, visualize_chat, "original"
            
            elif tool_name == "Visualize":
                # Switch to visualize mode
                if not visualize_chat:  # If visualize chat is empty, initialize it
                    new_visualize_chat = [
                        {
                            "role": "assistant",
                            "content": "📊 **Visualization Mode Activated**\n\nI'm now in visualization mode! I can help you:\n\n• Create charts and graphs from hospital data\n• Analyze patient statistics and trends\n• Generate visual reports and dashboards\n• Visualize medical data patterns\n\nWhat would you like to visualize or analyze?"
                        }
                    ]
                    display_chat = new_visualize_chat
                    stored_visualize_chat = new_visualize_chat
                else:
                    # Return to existing visualize chat with welcome back message for display only
                    display_chat = visualize_chat + [
                        {
                            "role": "assistant",
                            "content": "--- 📊 **Welcome back to Visualization Mode!**\n\n📋 You can see your previous visualization conversation history above, but please note that I'm starting with a fresh conversation context. I don't have access to the details from our previous messages, so feel free to provide any relevant context if you'd like to continue where we left off.\n\nWhat would you like to visualize or analyze today?"
                        }
                    ]
                    stored_visualize_chat = visualize_chat  # Keep original history without welcome message
                
                # Store current chat as original if we're switching from original mode
                if current_mode == "original":
                    original_chat = current_chat
                
                return "", display_chat, original_chat, stored_visualize_chat, "visualize"
              # For any other tools (shouldn't happen with current setup)
            return "", current_chat, original_chat, visualize_chat, current_mode

        test_dropdown.change(
            fn=handle_tool_selection,
            inputs=[test_dropdown, chatbot, original_chat_state, visualize_chat_state, current_mode_state],
            outputs=[msg, chatbot, original_chat_state, visualize_chat_state, current_mode_state],
        )        # Load welcome message
        demo.load(
            fn=lambda: [
                {
                    "role": "assistant",
                    "content": "🏥 Welcome to Health AI Hospital Aid (H.A.H.A)! I'm your Medical Assistant powered by advanced AI.\n\n**I can help you with:**\n• Health information and medical guidance\n• Hospital services and patient support\n• Medical consultations and advice\n• Health monitoring and analysis\n• Emergency assistance coordination\n\nFeel free to ask me any health-related questions or concerns!",
                }
            ],
            outputs=chatbot,        )

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
    
    <!-- Dashboard Enhancement Styles -->
    <style>
    /* Navigation Enhancements */
    .nav-buttons-container {
        display: flex !important;
        gap: 8px !important;
        margin-bottom: 24px !important;
        padding: 0 32px !important;
        background: white !important;
        border-bottom: 1px solid #e2e8f0 !important;
        padding-bottom: 16px !important;
    }

    .nav-btn {
        background: transparent !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        font-size: 14px !important;
        color: #64748b !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .nav-btn:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #475569 !important;
        transform: translateY(-1px) !important;
    }

    .nav-btn.active {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    /* Enhanced Metric Cards */
    .metric-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .metric-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 4px !important;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4) !important;
        transform: scaleX(0) !important;
        transition: transform 0.3s ease !important;
        transform-origin: left !important;
    }

    .metric-card:hover::before {
        transform: scaleX(1) !important;
    }

    .metric-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
    }

    /* Progress Circle Enhancements */
    .progress-circle-fill {
        transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .progress-text {
        font-family: 'SF Pro Display', -apple-system, sans-serif !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }

    .metric-card:hover .progress-text {
        transform: scale(1.1) !important;
        color: #3b82f6 !important;
    }

    /* Tool Usage Chart Enhancements */
    .bar {
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
        cursor: pointer !important;
        position: relative !important;
    }

    .bar:hover {
        background: linear-gradient(180deg, #1d4ed8, #3b82f6) !important;
        transform: scaleY(1.1) !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3) !important;
    }

    /* Staff Progress Bars Enhanced */
    .progress-fill {
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
    }

    .staff-percentage {
        font-weight: 600 !important;
        color: #3b82f6 !important;
        min-width: 45px !important;
        text-align: right !important;
        transition: all 0.3s ease !important;
    }

    .staff-item:hover .staff-percentage {
        transform: scale(1.1) !important;
        color: #1d4ed8 !important;
    }

    /* Notification Styles */
    .dashboard-notification {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        background: #10b981 !important;
        color: white !important;
        padding: 12px 20px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        z-index: 1000 !important;
        transform: translateX(100%) !important;
        transition: transform 0.3s ease !important;
        font-weight: 500 !important;
    }

         .dashboard-notification.show {
         transform: translateX(0) !important;
     }

     /* Content Sections */
     .content-container {
         position: relative !important;
         width: 100% !important;
         height: auto !important;
     }

     .content-section {
         display: none !important;
         opacity: 0 !important;
         transform: translateY(20px) !important;
         transition: all 0.3s ease !important;
     }

     .content-section.active {
         display: block !important;
         opacity: 1 !important;
         transform: translateY(0) !important;
     }

     /* Section Headers */
     .section-header {
         padding: 0 0 20px 0 !important;
         border-bottom: 1px solid #e2e8f0 !important;
         margin-bottom: 24px !important;
     }

     .section-header h2 {
         font-size: 24px !important;
         font-weight: 700 !important;
         color: #1e293b !important;
         margin: 0 !important;
     }

     /* Forecasting Styles */
     .forecast-card {
         background: linear-gradient(135deg, #f0f9ff, #e0f2fe) !important;
         border-left: 4px solid #10b981 !important;
     }

     .capacity-indicators {
         display: flex !important;
         flex-direction: column !important;
         gap: 12px !important;
     }

     .capacity-item {
         display: flex !important;
         justify-content: space-between !important;
         align-items: center !important;
         padding: 8px 0 !important;
     }

     .capacity-trend {
         font-weight: 600 !important;
         font-size: 14px !important;
     }

     .capacity-trend.up {
         color: #10b981 !important;
     }

     .capacity-trend.down {
         color: #ef4444 !important;
     }

     /* Alerts Styles */
     .alerts-header {
         display: flex !important;
         justify-content: space-between !important;
         align-items: center !important;
         padding: 0 0 20px 0 !important;
         border-bottom: 1px solid #e2e8f0 !important;
         margin-bottom: 24px !important;
     }

     .alert-summary {
         display: flex !important;
         gap: 16px !important;
     }

     .alert-count {
         padding: 6px 12px !important;
         border-radius: 20px !important;
         font-size: 12px !important;
         font-weight: 600 !important;
     }

     .alert-count.critical {
         background: #fef2f2 !important;
         color: #dc2626 !important;
     }

     .alert-count.warning {
         background: #fffbeb !important;
         color: #d97706 !important;
     }

     .alert-count.info {
         background: #eff6ff !important;
         color: #2563eb !important;
     }

     .alerts-list {
         display: flex !important;
         flex-direction: column !important;
         gap: 16px !important;
     }

     .alert-item {
         display: flex !important;
         gap: 16px !important;
         padding: 16px !important;
         background: white !important;
         border-radius: 8px !important;
         border-left: 4px solid #e2e8f0 !important;
         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
         transition: all 0.3s ease !important;
     }

     .alert-item:hover {
         transform: translateY(-2px) !important;
         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
     }

     .alert-item.critical {
         border-left-color: #dc2626 !important;
         background: #fef2f2 !important;
     }

     .alert-item.warning {
         border-left-color: #d97706 !important;
         background: #fffbeb !important;
     }

     .alert-item.info {
         border-left-color: #2563eb !important;
         background: #eff6ff !important;
     }

     .alert-icon {
         font-size: 20px !important;
         width: 24px !important;
         text-align: center !important;
     }

     .alert-content {
         flex: 1 !important;
     }

     .alert-content h4 {
         margin: 0 0 4px 0 !important;
         font-size: 16px !important;
         font-weight: 600 !important;
         color: #1e293b !important;
     }

     .alert-content p {
         margin: 0 0 8px 0 !important;
         color: #64748b !important;
         font-size: 14px !important;
     }

     .alert-time {
         font-size: 12px !important;
         color: #94a3b8 !important;
     }

     .alert-actions {
         display: flex !important;
         gap: 8px !important;
         align-items: flex-start !important;
     }

     .alert-btn {
         padding: 6px 12px !important;
         border-radius: 6px !important;
         font-size: 12px !important;
         font-weight: 500 !important;
         border: none !important;
         cursor: pointer !important;
         transition: all 0.2s ease !important;
     }

     .alert-btn.primary {
         background: #3b82f6 !important;
         color: white !important;
     }

     .alert-btn.primary:hover {
         background: #1d4ed8 !important;
     }

     .alert-btn {
         background: #f1f5f9 !important;
         color: #64748b !important;
     }

     .alert-btn:hover {
         background: #e2e8f0 !important;
     }

     /* Resources Styles */
     .resource-card {
         background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
         border-left: 4px solid #3b82f6 !important;
     }

     .equipment-grid {
         display: flex !important;
         flex-direction: column !important;
         gap: 12px !important;
     }

     .equipment-item {
         display: flex !important;
         justify-content: space-between !important;
         align-items: center !important;
         padding: 8px 0 !important;
     }

     .equipment-status.operational {
         color: #10b981 !important;
         font-weight: 600 !important;
     }

     .equipment-status.maintenance {
         color: #f59e0b !important;
         font-weight: 600 !important;
     }

     .inventory-list {
         display: flex !important;
         flex-direction: column !important;
         gap: 16px !important;
     }

     .inventory-item {
         display: flex !important;
         align-items: center !important;
         gap: 12px !important;
     }

     .inventory-name {
         min-width: 120px !important;
         font-size: 14px !important;
         color: #374151 !important;
     }

     .inventory-bar {
         flex: 1 !important;
         height: 8px !important;
         background: #f3f4f6 !important;
         border-radius: 4px !important;
         overflow: hidden !important;
     }

     .inventory-fill {
         height: 100% !important;
         transition: width 1s ease !important;
         border-radius: 4px !important;
     }

     .inventory-fill.good {
         background: #10b981 !important;
     }

     .inventory-fill.medium {
         background: #f59e0b !important;
     }

     .inventory-fill.low {
         background: #ef4444 !important;
     }

     .inventory-count {
         min-width: 40px !important;
         text-align: right !important;
         font-weight: 600 !important;
         font-size: 14px !important;
     }
    </style>

    <!-- Dashboard Enhancement JavaScript -->
    <script>
    class HospitalDashboard {
        constructor() {
            this.updateInterval = 30000; // 30 seconds
            this.metrics = {};
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
            this.initializeInteractiveChart();
            this.showWelcomeMessage();
        }

        initializeInteractiveChart() {
            // Initialize chart with default line chart
            setTimeout(() => {
                this.updateChart('line');
                
                // Ensure chart buttons are properly connected
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
            // Navigation buttons
            const observer = new MutationObserver(() => {
                const navBtns = document.querySelectorAll('.nav-btn');
                navBtns.forEach(btn => {
                    if (!btn.hasAttribute('data-listener')) {
                        btn.addEventListener('click', (e) => this.handleNavigation(e));
                        btn.setAttribute('data-listener', 'true');
                    }
                });

                // Metric cards hover effects
                const cards = document.querySelectorAll('.metric-card');
                cards.forEach(card => {
                    if (!card.hasAttribute('data-listener')) {
                        card.addEventListener('mouseenter', (e) => this.animateCard(e.target, true));
                        card.addEventListener('mouseleave', (e) => this.animateCard(e.target, false));
                        card.setAttribute('data-listener', 'true');
                    }
                });

                                 // Quick action buttons
                 const actionBtns = document.querySelectorAll('.quick-action-btn, .header-action-btn');
                 actionBtns.forEach(btn => {
                     if (!btn.hasAttribute('data-listener')) {
                         btn.addEventListener('click', (e) => this.handleQuickAction(e));
                         btn.setAttribute('data-listener', 'true');
                     }
                 });

                 // Alert action buttons
                 const alertBtns = document.querySelectorAll('.alert-btn');
                 alertBtns.forEach(btn => {
                     if (!btn.hasAttribute('data-listener')) {
                         btn.addEventListener('click', (e) => this.handleAlertAction(e));
                         btn.setAttribute('data-listener', 'true');
                     }
                 });

                 // Chart button interactions
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
                if (navBtns.length > 0 && !navBtns[0].classList.contains('active')) {
                    navBtns[0].classList.add('active');
                }
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

             // Switch content sections
             this.switchContentSection(section);
             this.loadSectionData(section);
         }

         switchContentSection(section) {
             // For now, always show the main analysis section
             // The navigation is just for visual feedback
             console.log(`Switched to ${section} section`);
             
             // Ensure main content area is always visible
             const mainContentArea = document.querySelector('.main-content-area');
             if (mainContentArea) {
                 mainContentArea.style.display = 'block';
                 mainContentArea.style.opacity = '1';
             }
             
             // Ensure analysis section is always visible
             const analysisSection = document.querySelector('.analysis-section');
             if (analysisSection) {
                 analysisSection.style.display = 'block';
                 analysisSection.style.opacity = '1';
             }
         }

                 loadSectionData(section) {
             console.log(`Loading ${section} section with simulated data...`);
             
             switch(section) {
                 case 'dashboard':
                     this.loadDashboardData();
                     this.showNotification('📊 Dashboard refreshed', 'success');
                     break;
                 case 'forecasting':
                     this.showNotification('📈 Forecasting data updated', 'info');
                     this.animateForecastCharts();
                     break;
                 case 'alerts':
                     this.showNotification('🚨 Alerts panel loaded', 'info');
                     this.updateAlertCounts();
                     break;
                 case 'resources':
                     this.showNotification('🏥 Resources data loaded', 'info');
                     this.animateResourceBars();
                     break;
             }
         }

         animateForecastCharts() {
             // Animate forecast chart if visible
             const forecastChart = document.querySelector('#forecasting-section .forecast-chart path');
             if (forecastChart) {
                 forecastChart.style.strokeDasharray = '500';
                 forecastChart.style.strokeDashoffset = '500';
                 setTimeout(() => {
                     forecastChart.style.strokeDashoffset = '0';
                 }, 300);
             }
         }

         updateAlertCounts() {
             // Update alert counts with random numbers
             const criticalCount = Math.floor(Math.random() * 5) + 1;
             const warningCount = Math.floor(Math.random() * 10) + 3;
             const infoCount = Math.floor(Math.random() * 15) + 8;

             const criticalEl = document.querySelector('.alert-count.critical');
             const warningEl = document.querySelector('.alert-count.warning');
             const infoEl = document.querySelector('.alert-count.info');

             if (criticalEl) criticalEl.textContent = `${criticalCount} Critical`;
             if (warningEl) warningEl.textContent = `${warningCount} Warnings`;
             if (infoEl) infoEl.textContent = `${infoCount} Info`;
         }

         animateResourceBars() {
             // Animate inventory bars
             const inventoryFills = document.querySelectorAll('#resources-section .inventory-fill');
             inventoryFills.forEach((fill, index) => {
                 const currentWidth = fill.style.width;
                 fill.style.width = '0%';
                 setTimeout(() => {
                     fill.style.width = currentWidth;
                 }, index * 200);
             });
         }

        showLoadingState(section) {
            const metricsContainer = document.querySelector('.metrics-container');
            if (metricsContainer) {
                metricsContainer.style.opacity = '0.7';
                setTimeout(() => {
                    metricsContainer.style.opacity = '1';
                }, 500);
            }
        }

        initializeCharts() {
            this.initICUOccupancyChart();
            this.initStaffAvailability();
            this.initToolUsageChart();
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
                        
                        // Update percentage displays
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
            // Simulate ICU occupancy changes
            const currentICU = this.metrics.icuOccupancy?.value || 71;
            const newICU = Math.max(50, Math.min(95, currentICU + (Math.random() - 0.5) * 10));
            this.updateICUOccupancy(Math.round(newICU));

            // Simulate staff availability changes
            const currentDoctors = this.metrics.staffAvailability?.doctors.value || 75;
            const currentNurses = this.metrics.staffAvailability?.nurses.value || 60;
            const newDoctors = Math.max(40, Math.min(90, currentDoctors + (Math.random() - 0.5) * 15));
            const newNurses = Math.max(30, Math.min(85, currentNurses + (Math.random() - 0.5) * 20));
            this.updateStaffAvailability(Math.round(newDoctors), Math.round(newNurses));

            // Simulate tool usage changes
            const newToolUsage = this.metrics.toolUsage?.values.map(val => 
                Math.max(20, Math.min(90, val + (Math.random() - 0.5) * 20))
            ) || [60, 40, 70, 35, 85];
            this.updateToolUsage(newToolUsage.map(val => Math.round(val)));
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

        animateCard(card, isHovering) {
            if (isHovering) {
                card.style.transform = 'translateY(-4px) scale(1.02)';
                card.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
            } else {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
            }
        }

                 handleQuickAction(event) {
             const button = event.target;
             const action = button.textContent.toLowerCase();
             
             const originalText = button.textContent;
             button.style.opacity = '0.7';
             button.textContent = 'Loading...';
             
             setTimeout(() => {
                 button.style.opacity = '1';
                 button.textContent = originalText;
                 
                 if (action.includes('status')) {
                     this.refreshAllMetrics();
                 }
             }, 1000);
         }

         handleAlertAction(event) {
             const button = event.target;
             const action = button.textContent.toLowerCase();
             const alertItem = button.closest('.alert-item');
             
             const originalText = button.textContent;
             button.style.opacity = '0.7';
             button.textContent = 'Processing...';
             
             setTimeout(() => {
                 button.style.opacity = '1';
                 button.textContent = originalText;
                 
                 if (action.includes('acknowledge') || action.includes('dispatch')) {
                     // Fade out the alert
                     alertItem.style.opacity = '0.5';
                     alertItem.style.transform = 'translateX(20px)';
                     this.showNotification(`Alert ${action}d successfully`, 'success');
                 } else if (action.includes('reorder')) {
                     this.showNotification('Reorder request submitted', 'success');
                 } else {
                     this.showNotification(`${action} action completed`, 'info');
                 }
             }, 1000);
         }

         handleChartTypeChange(event) {
             console.log('handleChartTypeChange called', event);
             const clickedBtn = event.target;
             const chartType = clickedBtn.getAttribute('data-chart') || clickedBtn.textContent.toLowerCase();
             
             console.log('Chart type detected:', chartType, 'from button:', clickedBtn.textContent);
             
             // Update active state
             document.querySelectorAll('.chart-btn').forEach(btn => {
                 btn.classList.remove('active');
             });
             clickedBtn.classList.add('active');
             
             // Show notification
             this.showNotification(`📊 Switched to ${clickedBtn.textContent} view`, 'info');
             
             // Update chart content
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

             // Use provided data or get current data
             const chartData = data || this.getChartData();
             console.log('Using chart data:', chartData);

             // Add transition effect
             chartContainer.style.opacity = '0.3';
             chartContainer.style.transform = 'scale(0.95)';
             
             setTimeout(() => {
                 // Generate chart based on type with dynamic data
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
                 
                 // Update legend dynamically
                 this.updateDynamicLegend(chartData, chartType);
                 
                 // Restore chart appearance
                 chartContainer.style.opacity = '1';
                 chartContainer.style.transform = 'scale(1)';
                 console.log('Chart updated successfully to', chartType);
             }, 150);
         }

         getCurrentChartData() {
             // Default sample data that can be easily replaced
             return [
                 { month: 'Jan', patients: 65, revenue: 45, paties: 50 },
                 { month: 'Feb', patients: 58, revenue: 52, paties: 45 },
                 { month: 'Mar', patients: 52, revenue: 58, paties: 40 },
                 { month: 'Apr', patients: 45, revenue: 62, paties: 35 },
                 { month: 'May', patients: 38, revenue: 68, paties: 30 },
                 { month: 'Jun', patients: 45, revenue: 55, paties: 25 },
                 { month: 'Jul', patients: 35, revenue: 48, paties: 20 }
             ];
         }

         analyzeDataStructure(data) {
             if (!data || data.length === 0) return { xField: null, yFields: [], colors: [] };
             
             const firstItem = data[0];
             const fields = Object.keys(firstItem);
             
             // Detect x-axis field (typically string/category field)
             const xField = fields.find(field => 
                 typeof firstItem[field] === 'string' || 
                 field.toLowerCase().includes('time') ||
                 field.toLowerCase().includes('date') ||
                 field.toLowerCase().includes('month') ||
                 field.toLowerCase().includes('category') ||
                 field.toLowerCase().includes('label')
             ) || fields[0];
             
             // Detect y-axis fields (numeric fields excluding x-axis)
             const yFields = fields.filter(field => 
                 field !== xField && 
                 typeof firstItem[field] === 'number'
             );
             
             // Generate colors dynamically
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

             // Calculate scales
             const allValues = data.flatMap(d => yFields.map(field => d[field] || 0));
             const minValue = Math.min(...allValues);
             const maxValue = Math.max(...allValues);
             const valueRange = maxValue - minValue || 1;
             
             // Scale functions
             const scaleY = (value) => 250 - ((value - minValue) / valueRange) * 180;
             const scaleX = (index) => 80 + index * (440 / (data.length - 1));

             return `
                 <svg width="100%" height="400" viewBox="0 0 600 300">
                     <!-- Grid lines -->
                     <defs>
                         <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                             <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                         </pattern>
                     </defs>
                     <rect width="100%" height="100%" fill="url(#grid)" />
                     
                     <!-- Y-axis labels -->
                     ${Array.from({length: 6}, (_, i) => {
                         const value = Math.round(maxValue - (i * valueRange / 5));
                         const y = 50 + i * 40;
                         return `<text x="30" y="${y}" fill="#64748b" font-size="12" text-anchor="end">${value}</text>`;
                     }).join('')}
                     
                     <!-- X-axis labels -->
                     ${data.map((d, i) => `<text x="${scaleX(i)}" y="280" fill="#64748b" font-size="12" text-anchor="middle">${d[xField]}</text>`).join('')}
                     
                     <!-- Dynamic lines for each field -->
                     ${yFields.map((field, fieldIndex) => {
                         const lineColor = colors[fieldIndex];
                         const pathData = data.map((d, i) => `${scaleX(i)} ${scaleY(d[field] || 0)}`).join(' L ');
                         return `
                             <!-- ${field} line -->
                             <path d="M ${pathData}" 
                                   stroke="${lineColor}" stroke-width="3" fill="none" stroke-linecap="round"/>
                             
                             <!-- Data points for ${field} -->
                             ${data.map((d, i) => `<circle cx="${scaleX(i)}" cy="${scaleY(d[field] || 0)}" r="4" fill="${lineColor}"/>`).join('')}
                         `;
                     }).join('')}
                 </svg>
             `;
         }

         // Keep old function for backwards compatibility
         generateLineChart() {
             return this.generateDynamicLineChart(this.getCurrentChartData());
         }

         generateDynamicBarChart(data) {
             const { xField, yFields, colors } = this.analyzeDataStructure(data);
             console.log('Bar chart structure:', { xField, yFields, colors });
             
             if (!xField || yFields.length === 0) {
                 return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid data structure for bar chart</div>';
             }

             // Calculate scales
             const allValues = data.flatMap(d => yFields.map(field => d[field] || 0));
             const minValue = Math.max(0, Math.min(...allValues)); // Start from 0 for bars
             const maxValue = Math.max(...allValues);
             const valueRange = maxValue - minValue || 1;
             
             // Scale functions
             const scaleY = (value) => 250 - ((value - minValue) / valueRange) * 180;
             const scaleHeight = (value) => ((value - minValue) / valueRange) * 180;
             const categoryWidth = 440 / data.length;
             const barWidth = Math.min(15, (categoryWidth - 10) / yFields.length);

             return `
                 <svg width="100%" height="400" viewBox="0 0 600 300">
                     <!-- Grid lines -->
                     <defs>
                         <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                             <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                         </pattern>
                     </defs>
                     <rect width="100%" height="100%" fill="url(#grid)" />
                     
                     <!-- Y-axis labels -->
                     ${Array.from({length: 6}, (_, i) => {
                         const value = Math.round(maxValue - (i * valueRange / 5));
                         const y = 50 + i * 40;
                         return `<text x="30" y="${y}" fill="#64748b" font-size="12" text-anchor="end">${value}</text>`;
                     }).join('')}
                     
                     <!-- X-axis labels -->
                     ${data.map((d, i) => {
                         const centerX = 80 + i * categoryWidth + categoryWidth / 2;
                         return `<text x="${centerX}" y="280" fill="#64748b" font-size="12" text-anchor="middle">${d[xField]}</text>`;
                     }).join('')}
                     
                     <!-- Dynamic bars for each field -->
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
                                 <!-- ${field} bar for ${d[xField]} -->
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

         // Keep old function for backwards compatibility
         generateBarChart() {
             return this.generateDynamicBarChart(this.getCurrentChartData());
         }

         generateDynamicPieChart(data) {
             console.log('Generating dynamic pie chart with data:', data);
             
             if (!data || data.length === 0) {
                 return '<div style="padding: 20px; text-align: center; color: #64748b;">No data available for pie chart</div>';
             }

             // For pie charts, we can use different approaches:
             // 1. If data has explicit value and label fields
             // 2. If data needs to be aggregated from multiple series
             // 3. Use the first numeric field for values
             
             const { xField, yFields, colors } = this.analyzeDataStructure(data);
             
             let pieData = [];
             
             // Check if we have explicit value/label structure
             if (data[0].hasOwnProperty('value') && data[0].hasOwnProperty('label')) {
                 pieData = data.map((d, i) => ({
                     label: d.label,
                     value: d.value,
                     color: d.color || colors[i % colors.length]
                 }));
             } else if (yFields.length === 1) {
                 // Single numeric field - use each data point as a slice
                 pieData = data.map((d, i) => ({
                     label: d[xField] || `Item ${i + 1}`,
                     value: d[yFields[0]] || 0,
                     color: colors[i % colors.length]
                 }));
             } else if (yFields.length > 1) {
                 // Multiple numeric fields - use field names as labels, sum values
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
                     <!-- Pie slices -->
                     ${slices.map(slice => `
                         <path d="${slice.path}" fill="${slice.color}" stroke="white" stroke-width="2"/>
                         ${slice.percentage > 5 ? `<text x="${slice.labelX}" y="${slice.labelY}" fill="white" font-size="12" text-anchor="middle" font-weight="600">${slice.percentage}%</text>` : ''}
                     `).join('')}
                     
                     <!-- Legend -->
                     ${pieData.map((d, i) => `
                         <rect x="450" y="${50 + i * 20}" width="12" height="12" fill="${d.color}" rx="2"/>
                         <text x="470" y="${60 + i * 20}" fill="#64748b" font-size="11">${d.label} (${Math.round((d.value / total) * 100)}%)</text>
                     `).join('')}
                     
                     <!-- Title -->
                     <text x="300" y="30" fill="#1e293b" font-size="16" text-anchor="middle" font-weight="600">Data Distribution</text>
                 </svg>
             `;
         }

         // Keep old function for backwards compatibility
         generatePieChart() {
             // Convert current data format to pie chart format for demo
             const currentData = this.getCurrentChartData();
             const { yFields, colors } = this.analyzeDataStructure(currentData);
             
             // Use field totals for pie chart
             const pieData = yFields.map((field, i) => ({
                 label: field.charAt(0).toUpperCase() + field.slice(1),
                 value: currentData.reduce((sum, d) => sum + (d[field] || 0), 0),
                 color: colors[i % colors.length]
             }));
             
             return this.generateDynamicPieChart(pieData);
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

             // Use first two numeric fields for X and Y axes
             const xAxisField = yFields[0];
             const yAxisField = yFields[1];
             const sizeField = yFields[2] || null; // Optional third field for bubble size
             const labelField = xField; // Use the category field for labels
             
             // Calculate scales
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
             
             // Scale functions
             const scaleX = (value) => 50 + ((value - xMin) / xRange) * 500;
             const scaleY = (value) => 250 - ((value - yMin) / yRange) * 200;
             const scaleSize = (value) => sizeField ? 
                 5 + ((value - sizeMin) / sizeRange) * 10 : 
                 8; // Default size if no size field

             return `
                 <svg width="100%" height="400" viewBox="0 0 600 300">
                     <!-- Grid lines -->
                     <defs>
                         <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                             <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                         </pattern>
                     </defs>
                     <rect width="100%" height="100%" fill="url(#grid)" />
                     
                     <!-- X-axis -->
                     <line x1="50" y1="250" x2="550" y2="250" stroke="#e2e8f0" stroke-width="2"/>
                     <text x="300" y="290" fill="#64748b" font-size="12" text-anchor="middle">${xAxisField.charAt(0).toUpperCase() + xAxisField.slice(1)}</text>
                     
                     <!-- Y-axis -->
                     <line x1="50" y1="50" x2="50" y2="250" stroke="#e2e8f0" stroke-width="2"/>
                     <text x="25" y="150" fill="#64748b" font-size="12" text-anchor="middle" transform="rotate(-90 25 150)">${yAxisField.charAt(0).toUpperCase() + yAxisField.slice(1)}</text>
                     
                     <!-- X-axis labels -->
                     ${Array.from({length: 6}, (_, i) => {
                         const value = Math.round(xMin + (i * xRange / 5));
                         const x = 50 + i * 100;
                         return `<text x="${x}" y="265" fill="#64748b" font-size="10" text-anchor="middle">${value}</text>`;
                     }).join('')}
                     
                     <!-- Y-axis labels -->
                     ${Array.from({length: 6}, (_, i) => {
                         const value = Math.round(yMax - (i * yRange / 5));
                         const y = 50 + i * 40;
                         return `<text x="35" y="${y}" fill="#64748b" font-size="10" text-anchor="end">${value}</text>`;
                     }).join('')}
                     
                     <!-- Scatter points -->
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
                     
                     <!-- Title -->
                     <text x="300" y="30" fill="#1e293b" font-size="16" text-anchor="middle" font-weight="600">${yAxisField.charAt(0).toUpperCase() + yAxisField.slice(1)} vs ${xAxisField.charAt(0).toUpperCase() + xAxisField.slice(1)}</text>
                 </svg>
             `;
         }

         // Keep old function for backwards compatibility
         generateScatterChart() {
             return this.generateDynamicScatterChart(this.getCurrentChartData());
         }

                 updateDynamicLegend(data, chartType) {
             const legendContainer = document.querySelector('.chart-legend');
             if (!legendContainer) return;

             const { xField, yFields, colors } = this.analyzeDataStructure(data);
             
             let legendHTML = '';
             
             if (chartType === 'pie') {
                 // For pie charts, show different legend format
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
                 // For scatter charts, show the axes being compared
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
                 // For line and bar charts, show all numeric fields
                 legendHTML = yFields.map((field, i) => `
                     <span class="legend-item">
                         <span class="legend-color" style="background: ${colors[i]};"></span>
                         ${field.charAt(0).toUpperCase() + field.slice(1)}
                     </span>
                 `).join('');
             }
             
             legendContainer.innerHTML = legendHTML;
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
                
                // Final fallback to ensure chart interactivity
                this.ensureChartInteractivity();
            }, 1000);
        }

        ensureChartInteractivity() {
            console.log('Ensuring chart interactivity...');
            
            // Force initialize chart
            const chartContainer = document.querySelector('.line-chart');
            if (chartContainer && !chartContainer.hasAttribute('data-initialized')) {
                console.log('Force initializing chart...');
                this.updateChart('line');
                chartContainer.setAttribute('data-initialized', 'true');
            }
            
            // Ensure all chart buttons have click handlers
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
        }

        // Method to update chart data externally
        setChartData(newData) {
            console.log('Setting new chart data:', newData);
            this.chartData = newData;
            
            // Re-render current chart with new data
            const activeBtn = document.querySelector('.chart-btn.active');
            if (activeBtn) {
                const chartType = activeBtn.getAttribute('data-chart') || 'line';
                this.updateChart(chartType, newData);
            }
        }

        // Get current chart data (with fallback)
        getChartData() {
            return this.chartData || this.getCurrentChartData();
        }

        loadDashboardData() {
            console.log('Loading dashboard data...');
            this.simulateDataUpdate();
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

    // Additional immediate initialization for chart interactivity
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, setting up chart interactivity immediately...');
        
        // Wait a moment for Gradio to finish rendering
        setTimeout(() => {
            // Find chart buttons and add click handlers directly
            const chartButtons = document.querySelectorAll('.chart-btn');
            console.log('Direct setup: Found', chartButtons.length, 'chart buttons');
            
            chartButtons.forEach((btn, index) => {
                console.log('Setting up button', index, ':', btn.textContent);
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const chartType = this.getAttribute('data-chart') || this.textContent.toLowerCase();
                    console.log('Direct click handler - Chart type:', chartType);
                    
                    // Update active state
                    chartButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Update chart
                    if (window.hospitalDashboard) {
                        window.hospitalDashboard.updateChart(chartType);
                        window.hospitalDashboard.showNotification(`📊 Switched to ${this.textContent} view`, 'info');
                    }
                });
            });
            
            // Initialize with line chart
            if (window.hospitalDashboard) {
                console.log('Direct initialization with line chart');
                window.hospitalDashboard.updateChart('line');
            }
        }, 2000);
    });
    </script>
    """


def load_modern_hospital_css():
    """Load modern hospital CSS for the interface"""
    return """
    /* HOSPITAL DASHBOARD - OPTIMIZED LAYOUT */
    
    /* Reset and force proper layout */
    .gradio-container {
        max-width: 100vw !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 0 !important;
        background: #f8fafc !important;
        height: 100vh !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Main container - FIXED LAYOUT */
    .main-container {
        display: flex !important;
        height: 100vh !important;
        width: 100% !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }
    
    /* Left Sidebar - FIXED AND VISIBLE */
    .sidebar-container {
        width: 350px !important;
        min-width: 350px !important;
        max-width: 350px !important;
        height: 100vh !important;
        background: white !important;
        border-right: 1px solid #e2e8f0 !important;
        display: flex !important;
        flex-direction: column !important;
        flex-shrink: 0 !important;
        overflow: visible !important;
        position: relative !important;
    }
    
    /* Assistant Header - Compact and clean */
    .assistant-header {
        padding: 20px !important;
        border-bottom: 1px solid #f1f5f9 !important;
        background: white !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        flex-shrink: 0 !important;
    }
    
    .avatar-circle {
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-size: 20px !important;
        flex-shrink: 0 !important;
    }
    
    .assistant-text h3 {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin: 0 0 2px 0 !important;
    }
    
    .assistant-text p {
        font-size: 13px !important;
        color: #64748b !important;
        margin: 0 !important;
    }
    
    /* Model Dropdown - Blue Background with White Text (STRONGER TARGETING) */
    .sidebar-container .gradio-dropdown,
    .sidebar-container .gradio-dropdown > div,
    .sidebar-container .gradio-dropdown div,
    .sidebar-container [data-testid="dropdown"],
    .sidebar-container [data-testid="dropdown"] > div,
    .sidebar-container [data-testid="dropdown"] div,
    .sidebar-container .wrap,
    .sidebar-container .wrap > div {
        background: #3b82f6 !important;
        background-color: #3b82f6 !important;
        border: none !important;
        border-radius: 8px !important;
        margin: 16px 20px 12px 20px !important;
    }
    
    .sidebar-container .gradio-dropdown button,
    .sidebar-container .gradio-dropdown select,
    .sidebar-container [data-testid="dropdown"] button,
    .sidebar-container [data-testid="dropdown"] div,
    .sidebar-container .wrap button,
    .sidebar-container [role="button"],
    .sidebar-container .svelte-select,
    .sidebar-container .svelte-select button {
        background: #3b82f6 !important;
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
    }
      /* Force all elements in dropdown to be blue with white text (ONLY DROPDOWN) */
    .sidebar-container .gradio-dropdown *:not([data-testid="chatbot"]):not([class*="chatbot"]),
    .sidebar-container [class*="dropdown"]:not([class*="chatbot"]) * {
        color: white !important;
    }
    
    /* ENSURE model dropdown area only affects dropdown, not chat */
    .sidebar-container > *:first-child .gradio-dropdown,
    .sidebar-container > *:first-child [class*="dropdown"] {
        background: #3b82f6 !important;
        background-color: #3b82f6 !important;
    }
    
    /* NUCLEAR OPTION: FORCE WHITE CHAT BACKGROUND - OVERRIDE EVERYTHING */
    .sidebar-container .gradio-chatbot,
    .sidebar-container [data-testid="chatbot"],
    .sidebar-container .gradio-chatbot *,
    .sidebar-container [data-testid="chatbot"] * {
        background: white !important;
        background-color: white !important;
        color: black !important;
    }
    
    /* Override specific blue background that's being applied */
    .sidebar-container [style*="background: rgb(59, 130, 246)"] {
        background: white !important;
        background-color: white !important;
    }
    
    /* Override any blue background inline styles in chat */
    .sidebar-container .gradio-chatbot[style],
    .sidebar-container [data-testid="chatbot"][style] {
        background: white !important;
        background-color: white !important;
    }
    
    /* Make sure chat container itself is white */
    .sidebar-container > * > .gradio-chatbot,
    .sidebar-container > * > [data-testid="chatbot"] {
        background: white !important;
        background-color: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        margin: 12px 20px !important;
    }
    
    /* Force white background on any element that might be blue */
    .sidebar-container [class*="chatbot"] {
        background: white !important;
        background-color: white !important;
        color: black !important;
    }
    
    /* Chat Interface - Light Background with Black Text (SELECTIVE TARGETING) */
    .sidebar-container .gradio-chatbot,
    .sidebar-container [data-testid="chatbot"] {
        background: white !important;
        background-color: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        margin: 12px 20px !important;
    }
    
    /* Chat messages should have light background and dark text (EXCLUDE dropdowns) */
    .sidebar-container .gradio-chatbot div:not([class*="dropdown"]):not([class*="select"]),
    .sidebar-container [data-testid="chatbot"] div:not([class*="dropdown"]):not([class*="select"]) {
        background: #f8fafc !important;
        background-color: #f8fafc !important;
        color: #1f2937 !important;
        border: none !important;
        border-radius: 6px !important;
        margin: 4px !important;
        padding: 8px !important;
    }
    
    /* Ensure chat text is dark (EXCLUDE dropdowns) */
    .sidebar-container .gradio-chatbot p,
    .sidebar-container .gradio-chatbot span,
    .sidebar-container [data-testid="chatbot"] p,
    .sidebar-container [data-testid="chatbot"] span {
        color: #1f2937 !important;
        background: transparent !important;
    }
    
    /* Chat Input Area - Clean and Modern */
    .sidebar-container .gradio-textbox,
    .sidebar-container [data-testid="textbox"] {
        background: #f8fafc !important;
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1f2937 !important;
        margin: 12px 20px !important;
    }
    
    .sidebar-container .gradio-textbox:focus,
    .sidebar-container [data-testid="textbox"]:focus {
        border-color: #3b82f6 !important;
        background: white !important;
        background-color: white !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }
    
    .sidebar-container .gradio-button,
    .sidebar-container [data-testid="button"] {
        background: #3b82f6 !important;
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        margin: 12px 8px 12px 0 !important;
        transition: all 0.2s ease !important;
    }
    
    .sidebar-container .gradio-button:hover,
    .sidebar-container [data-testid="button"]:hover {
        background: #2563eb !important;
        background-color: #2563eb !important;
        transform: translateY(-1px) !important;
    }
    
    /* Right Dashboard - EXPANDED AND CENTERED */
    .dashboard-container {
        flex: 1 !important;
        height: 100vh !important;
        background: #f8fafc !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        position: relative !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Dashboard Header - Compact */
    .dashboard-header-compact {
        background: white !important;
        padding: 12px 32px !important;
        border-bottom: 1px solid #e2e8f0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        flex-shrink: 0 !important;
        min-height: 60px !important;
    }
    
    .dashboard-title-compact h1 {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.5px !important;
        margin: 0 0 2px 0 !important;
        line-height: 1.2 !important;
    }
    
    .dashboard-title-compact p {
        font-size: 13px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    
    /* Header Controls - Compact */
    .dashboard-controls-compact {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
    }
    
    .header-dropdown {
        min-width: 200px !important;
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }
    
    .header-action-btn {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }
    
    .header-action-btn:hover {
        background: #2563eb !important;
        transform: translateY(-1px) !important;
    }
    
    /* Navigation Buttons */
    .nav-buttons-container {
        background: white !important;
        padding: 8px 32px 12px 32px !important;
        border-bottom: 1px solid #e2e8f0 !important;
        display: flex !important;
        gap: 8px !important;
        flex-shrink: 0 !important;
    }
    
    .nav-btn {
        background: transparent !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        color: #64748b !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }
    
    .nav-btn.active {
        background: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }
    
    .nav-btn:hover {
        background: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #475569 !important;
    }
    
    .nav-btn.active:hover {
        background: #2563eb !important;
        color: white !important;
    }
    
    /* Metrics Container - PERFECTLY BALANCED */
    .metrics-container {
        flex: 1 !important;
        padding: 24px 32px !important;
        overflow-y: auto !important;
        display: block !important;
    }
    
    .metrics-row {
        display: flex !important;
        gap: 20px !important;
        margin-bottom: 20px !important;
        width: 100% !important;
        flex-wrap: nowrap !important;
    }
    
    .metric-card {
        flex: 1 !important;
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
        overflow: hidden !important;
        min-height: 180px !important;
        min-width: 250px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    .metric-card h3 {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin: 12px 0 6px 0 !important;
    }
    
    .card-subtitle {
        font-size: 12px !important;
        color: #64748b !important;
        margin: 4px 0 0 0 !important;
    }
    
    /* Progress Circle (ICU Occupancy) */
    .progress-circle {
        position: relative !important;
        width: 100px !important;
        height: 100px !important;
        margin: 0 auto 12px auto !important;
        display: block !important;
    }
    
    .progress-circle svg {
        transform: rotate(-90deg) !important;
        display: block !important;
    }
    
    .progress-circle-bg {
        fill: none !important;
        stroke: #f1f5f9 !important;
        stroke-width: 8 !important;
    }
    
    .progress-circle-fill {
        fill: none !important;
        stroke: #3b82f6 !important;
        stroke-width: 8 !important;
        stroke-linecap: round !important;
        stroke-dasharray: 283 !important;
        stroke-dashoffset: 82 !important;
        transition: stroke-dashoffset 0.3s ease !important;
    }
    
    .progress-text {
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    /* Load Chart (Emergency Room Load) */
    .load-chart {
        width: 180px !important;
        height: 70px !important;
        margin: 0 auto 12px auto !important;
        display: block !important;
    }
    
    .load-path {
        stroke: #3b82f6 !important;
        stroke-width: 3 !important;
        fill: none !important;
    }
    
    .load-area {
        fill: url(#gradient) !important;
    }
    
    /* Staff Metrics */
    .staff-metrics {
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        width: 180px !important;
        margin: 12px auto 0 auto !important;
    }
    
    .staff-item {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        width: 100% !important;
    }
    
    .staff-label {
        font-size: 12px !important;
        font-weight: 500 !important;
        color: #475569 !important;
        min-width: 50px !important;
        text-align: left !important;
    }
    
    .progress-bar {
        flex: 1 !important;
        height: 6px !important;
        background: #f1f5f9 !important;
        border-radius: 3px !important;
        overflow: hidden !important;
        position: relative !important;
    }
    
    .progress-fill {
        height: 100% !important;
        border-radius: 3px !important;
        transition: width 0.3s ease !important;
        display: block !important;
    }
    
    .doctors-progress {
        width: 75% !important;
        background: #3b82f6 !important;
    }
    
    .nurses-progress {
        width: 60% !important;
        background: #3b82f6 !important;
    }
    
    .staff-percentage {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #3b82f6 !important;
        min-width: 28px !important;
        text-align: right !important;
    }
    
    /* Tool Usage Chart */
    .usage-chart {
        display: flex !important;
        align-items: end !important;
        justify-content: center !important;
        gap: 6px !important;
        height: 70px !important;
        width: 140px !important;
        margin: 0 auto 12px auto !important;
    }
    
    .bar {
        width: 14px !important;
        background: #3b82f6 !important;
        border-radius: 2px 2px 0 0 !important;
        transition: all 0.3s ease !important;
        opacity: 0.8 !important;
        display: block !important;
    }
    
    .bar:hover {
        opacity: 1 !important;
        background: #2563eb !important;
    }
    
    .bar:nth-child(1) { height: 60% !important; }
    .bar:nth-child(2) { height: 40% !important; }
    .bar:nth-child(3) { height: 70% !important; }
    .bar:nth-child(4) { height: 35% !important; }
    .bar:nth-child(5) { height: 85% !important; }
    
    /* Settings Panel */
    .dashboard-settings {
        margin: 16px 32px 32px 32px !important;
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    
    .settings-dropdown, .settings-slider {
        margin: 8px 0 !important;
        background: white !important;
    }
    
    .context-input {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background: white !important;
        resize: vertical !important;
        margin-top: 12px !important;
        font-size: 14px !important;
        padding: 10px 12px !important;
    }
    
    .context-input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Hide Gradio elements that interfere */
    .footer {
        display: none !important;
    }
    
    /* Force overrides for Gradio layout quirks */
    .gradio-row {
        gap: 0 !important;
        margin: 0 !important;
    }
    
    .gradio-column {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .gradio-accordion {
        border: none !important;
    }
    
    /* Removed problematic chatbot CSS - using Gradio defaults */
    
    /* Responsive Design */
    @media (max-width: 1200px) {
        .main-container {
            max-width: 100% !important;
        }
        
        .sidebar-container {
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
        }
        
        .metrics-row {
            gap: 16px !important;
        }
        
        .dashboard-header-row {
            padding: 16px 24px !important;
        }
    }
    
    @media (max-width: 768px) {
        .main-container {
            flex-direction: column !important;
        }
        
        .sidebar-container {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            height: 50vh !important;
            border-right: none !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        
        .dashboard-container {
            height: 50vh !important;
        }
        
        .metrics-row {
            flex-direction: column !important;
            gap: 12px !important;
        }
        
        .dashboard-header-row {
            padding: 12px 16px !important;
            flex-direction: column !important;
            gap: 12px !important;
            align-items: flex-start !important;
        }
        
        .dashboard-controls {
            align-self: stretch !important;
            justify-content: space-between !important;
        }
        
        .dashboard-title h1 {
            font-size: 22px !important;
        }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: #f8fafc !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1 !important;
        border-radius: 3px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8 !important;
    }
    
    /* CRITICAL: Force visibility and centering */
    .gradio-container * {
        box-sizing: border-box !important;
    }
    
    /* Force all elements to be visible */
    .metric-card, .metrics-row, .metrics-container {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
    }
    
    .metrics-row {
        display: flex !important;
    }
    
    /* Center the entire interface */
    body {
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }
    /* GUIDANCE TEXT STYLING */
    .guidance-text {
        padding: 16px 20px !important;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
        border: 1px solid #e0f2fe !important;
        border-radius: 12px !important;
        margin: 16px 20px !important;
        color: #0f172a !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
    }

    .guidance-text p {
        margin: 0 0 8px 0 !important;
        color: #334155 !important;
    }

    /* HELPLINE BUTTON STYLING - COMPACT */
    .helpline-btn-compact {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25) !important;
        transition: all 0.2s ease !important;
        min-width: 90px !important;
        height: 36px !important;
    }

    .helpline-btn-compact:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35) !important;
    }

    /* MAIN CONTENT AREA STYLING */
    .main-content-area {
        flex: 1 !important;
        display: block !important;
        background: #f8fafc !important;
        min-height: 500px !important;
        max-height: calc(100vh - 120px) !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    /* ANALYSIS SECTION STYLING */
    .analysis-section {
        padding: 20px 24px !important;
        background: white !important;
        margin: 0 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    .analysis-title {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin: 0 0 20px 0 !important;
        font-style: italic !important;
    }

    /* CHART CONTROLS STYLING */
    .chart-controls {
        display: flex !important;
        gap: 8px !important;
        margin-bottom: 24px !important;
    }

    .chart-btn {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #64748b !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    .chart-btn.active {
        background: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }

    .chart-btn:hover:not(.active) {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #475569 !important;
    }

    /* CHART CONTAINER STYLING */
    .chart-container {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 400px !important;
        max-height: 400px !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }

    .chart-legend {
        margin-bottom: 16px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    .legend-item {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        font-size: 14px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        margin-right: 20px !important;
    }

    .legend-color {
        width: 12px !important;
        height: 12px !important;
        border-radius: 2px !important;
        display: block !important;
    }

    .line-chart {
        width: 100% !important;
        height: 320px !important;
        max-width: 100% !important;
        overflow: hidden !important;
        display: block !important;
        box-sizing: border-box !important;
    }

    .line-chart svg {
        width: 100% !important;
        height: 100% !important;
        max-width: 100% !important;
        display: block !important;
        transition: opacity 0.3s ease, transform 0.3s ease !important;
    }

    /* Chart transition effects */
    .line-chart {
        transition: opacity 0.3s ease, transform 0.3s ease !important;
    }

    /* Enhanced chart button hover effects */
    .chart-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    /* Chart interactive elements */
    .line-chart svg circle {
        transition: r 0.2s ease, opacity 0.2s ease !important;
        cursor: pointer !important;
    }

    .line-chart svg circle:hover {
        r: 6 !important;
        opacity: 0.8 !important;
    }

    .line-chart svg rect {
        transition: opacity 0.2s ease, transform 0.2s ease !important;
        cursor: pointer !important;
    }

    .line-chart svg rect:hover {
        opacity: 0.8 !important;
        transform: scale(1.05) !important;
    }

    .line-chart svg path[fill*="#"] {
        transition: opacity 0.2s ease !important;
        cursor: pointer !important;
    }    .line-chart svg path[fill*="#"]:hover {
        opacity: 0.8 !important;
    }

    /* ENHANCED CHATBOT - PREMIUM MESSAGING INTERFACE */
    .chatbot-gr-chatbot {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        overflow: hidden !important;
        position: relative !important;
    }

    .chatbot-gr-chatbot::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4) !important;
    }
    
    .chatbot-gr-chatbot .bubble-wrap {
        background: transparent !important;
        padding: 8px 12px !important;
        margin: 6px 0 !important;
        border-radius: 14px !important;
        position: relative !important;
        transition: all 0.2s ease !important;
    }
    
    /* ASSISTANT MESSAGE - SOPHISTICATED BLUE GRADIENT */
    .chatbot-gr-chatbot .message.bot {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 85%, #1d4ed8 100%) !important;
        color: white !important;
        box-shadow: 0 3px 12px rgba(59, 130, 246, 0.25) !important;
        border: none !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .chatbot-gr-chatbot .message.bot::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent) !important;
        transition: left 0.5s ease !important;
    }

    .chatbot-gr-chatbot .message.bot:hover::before {
        left: 100% !important;
    }

    .chatbot-gr-chatbot .message.bot:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35) !important;
    }
    
    /* USER MESSAGE - ELEGANT LIGHT BLUE SHADE */
    .chatbot-gr-chatbot .message.user {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 85%, #93c5fd 100%) !important;
        color: #1e293b !important; /* Changed color to a darker shade for better contrast */
        border: 1px solid #93c5fd !important;
        box-shadow: 0 2px 8px rgba(147, 197, 253, 0.2) !important;
        font-weight: 500 !important;
        position: relative !important;
    }

    .chatbot-gr-chatbot .message.user:hover {
        background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 85%, #60a5fa 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(147, 197, 253, 0.3) !important;
    }

    /* ICON BUTTONS - REFINED ACCENT COLORS */
    .chatbot-gr-chatbot .icon-button-wrapper {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(6, 182, 212, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    .chatbot-gr-chatbot .icon-button-wrapper:hover {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
    }
    
    .chatbot-gr-chatbot .icon-button-wrapper button {
        background: transparent !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }

    /* ENHANCED INPUT CONTAINER - MODERN CHAT INPUT */
    #component-6 {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
        padding: 0 !important;
    }

    #component-6 .input-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 4px 16px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    #component-6 .input-container::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.05), transparent) !important;
        transition: left 0.6s ease !important;
    }

    #component-6 .input-container:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), 0 4px 12px rgba(59, 130, 246, 0.15) !important;
        transform: translateY(-1px) !important;
    }

    #component-6 .input-container:focus-within::before {
        left: 100% !important;
    }
    
    #component-6 .input-container textarea {
        background: transparent !important;
        border: none !important;
        outline: none !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        margin: 0 !important;
        padding: 8px 0 !important;
        resize: none !important;
    }

    #component-6 .input-container textarea::placeholder {
        color: #94a3b8 !important;
        font-weight: 400 !important;
    }
    
    /* ENHANCED SEND BUTTON - PREMIUM ACTION BUTTON */
    #component-6 button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        width: 40px !important;
        height: 40px !important;
        max-height: 40px !important;
        max-width: 40px !important;
        min-height: 40px !important;
        min-width: 40px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    #component-6 button::before {
        content: '' !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        width: 0 !important;
        height: 0 !important;
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 50% !important;
        transform: translate(-50%, -50%) !important;
        transition: width 0.3s ease, height 0.3s ease !important;
    }

    #component-6 button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
    }

    #component-6 button:hover::before {
        width: 30px !important;
        height: 30px !important;
    }

    #component-6 button:active {
        transform: translateY(0) scale(0.95) !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }

    /* ENHANCED FOCUS STATES AND ACCESSIBILITY */
    .model-gr-dropdown:focus-within,
    .chatbot-gr-chatbot:focus-within,
    #component-6 button:focus {
        outline: 2px solid #3b82f6 !important;
        outline-offset: 2px !important;
    }

    /* SUBTLE ANIMATIONS FOR ENHANCED INTERACTIVITY */
    @keyframes messageSlideIn {
        from {
            opacity: 0 !important;
            transform: translateY(10px) !important;
        }
        to {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    }

    .chatbot-gr-chatbot .message {
        animation: messageSlideIn 0.3s ease-out !important;
    }

    /* LOADING STATES */
    .chatbot-gr-chatbot .message.loading {
        background: linear-gradient(90deg, #f1f5f9, #e2e8f0, #f1f5f9) !important;
        background-size: 200% 100% !important;
        animation: shimmer 1.5s infinite !important;
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* ===== CHATBOT LOADER INTEGRATION STYLES ===== */
    
    /* Loading Indicator Container */
    .loading-indicator {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        padding: 16px 20px !important;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        margin: 8px 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        position: relative !important;
        overflow: hidden !important;
        animation: loadingSlideIn 0.3s ease-out !important;
    }

    /* Loading Indicator Shimmer Effect */
    .loading-indicator::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.08), transparent) !important;
        animation: loadingShimmer 2s infinite !important;
    }

    /* Animated Loading Dots */
    .loading-dots {
        display: inline-block !important;
        width: 20px !important;
        height: 14px !important;
        position: relative !important;
    }

    .loading-dots::after {
        content: '•••' !important;
        display: inline-block !important;
        color: #3b82f6 !important;
        font-size: 16px !important;
        letter-spacing: 2px !important;
        animation: loadingDots 1.4s infinite ease-in-out !important;
    }

    /* Loading Animations */
    @keyframes loadingSlideIn {
        from {
            opacity: 0 !important;
            transform: translateY(10px) scale(0.95) !important;
        }
        to {
            opacity: 1 !important;
            transform: translateY(0) scale(1) !important;
        }
    }

    @keyframes loadingShimmer {
        0% { 
            left: -100% !important;
        }
        100% { 
            left: 100% !important;
        }
    }

    @keyframes loadingDots {
        0%, 80%, 100% {
            opacity: 0.3 !important;
            transform: scale(0.8) !important;
        }
        40% {
            opacity: 1 !important;
            transform: scale(1) !important;
        }
    }

    /* Enhanced Loading States for Different Types */
    .loading-indicator[data-type="thinking"] {
        border-left: 4px solid #8b5cf6 !important;
    }

    .loading-indicator[data-type="database"] {
        border-left: 4px solid #06b6d4 !important;
    }

    .loading-indicator[data-type="ai"] {
        border-left: 4px solid #10b981 !important;
    }

    .loading-indicator[data-type="generating"] {
        border-left: 4px solid #f59e0b !important;
    }

    /* Responsive Loading Indicator */
    @media (max-width: 768px) {
        .loading-indicator {
            padding: 12px 16px !important;
            font-size: 13px !important;
            margin: 6px 0 !important;
        }
        
        .loading-dots::after {
            font-size: 14px !important;
        }
    }

    /* Dark Mode Support for Loading Indicator */
    @media (prefers-color-scheme: dark) {
        .loading-indicator {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            border-color: #475569 !important;
            color: #cbd5e1 !important;
        }
        
        .loading-indicator::before {
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.15), transparent) !important;
        }
    }

    /* Accessibility Enhancements */
    .loading-indicator[aria-live="polite"] {
        position: relative !important;
    }

    /* Reduced Motion Support */
    @media (prefers-reduced-motion: reduce) {
        .loading-indicator,
        .loading-indicator::before,
        .loading-dots::after {
            animation: none !important;
        }
        
        .loading-dots::after {
            content: '...' !important;
        }
    }

    /* Additional Responsive Design for Chart Layout */
    @media (max-width: 1200px) {
        .analysis-section {
            padding: 16px 20px !important;
        }
        
        .chart-container {
            padding: 12px !important;
            height: 350px !important;
        }
        
        .line-chart {
            height: 280px !important;
        }
        
        .dashboard-container {
            overflow-x: hidden !important;
        }
    }

    @media (max-width: 768px) {
        .analysis-section {
            padding: 12px 16px !important;
        }
        
        .chart-container {
            padding: 8px !important;
            height: 300px !important;
        }
        
        .line-chart {
            height: 240px !important;
        }        .chart-controls {
            flex-wrap: wrap !important;
            gap: 6px !important;
        }

        .chart-btn {
            padding: 6px 12px !important;
            font-size: 12px !important;
        }
    }    /* CUSTOM TEST DROPDOWN STYLES - COMPREHENSIVE GRADIO TARGETING */
    .custom-dropdown-container {
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 9999 !important;
        width: 200px !important;
        background: none !important;
        border: none !important;
    }
      /* DROPDOWN BUTTON - TARGET ALL POSSIBLE GRADIO SELECTORS */
    .custom-test-dropdown,
    .custom-test-dropdown .gradio-dropdown,
    .custom-test-dropdown [data-testid="dropdown"],
    .custom-test-dropdown .svelte-select,
    .custom-test-dropdown button,
    .custom-test-dropdown select {
        background-color: #4883FF !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(72, 131, 255, 0.3) !important;
        width: 100% !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 8px 12px 8px 32px !important;
        background-image: url('static/images/tools.svg') !important;
        background-repeat: no-repeat !important;
        background-position: 8px center !important;
        background-size: 16px 16px !important;
    }
      /* REMOVE WRAPPER STYLING - CLEAN BUTTON APPEARANCE */
    .custom-test-dropdown .wrap,
    .custom-test-dropdown .wrap > div:first-child {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 0 !important;
    }
    
    /* REMOVE ALL ADDITIONAL CONTAINER STYLING */
    .custom-test-dropdown > div,
    .custom-test-dropdown .wrap > div,
    .custom-test-dropdown [data-testid="dropdown"] > div,
    .custom-test-dropdown .dropdown-container,
    .custom-test-dropdown .dropdown-wrapper {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 0 !important;
        outline: none !important;
    }
      /* DROPDOWN TEXT/CONTENT STYLING */
    .custom-test-dropdown span,
    .custom-test-dropdown .wrap span,
    .custom-test-dropdown [data-testid="dropdown"] span,
    .custom-test-dropdown button span,
    .custom-test-dropdown select option,
    .custom-test-dropdown .value,
    .custom-test-dropdown .selected-value,
    .custom-test-dropdown .dropdown-text,
    .custom-test-dropdown .selection,
    .custom-test-dropdown .current-selection {
        background-color: transparent !important;
        color: white !important;
        font-weight: 500 !important;
    }
      /* FORCE WHITE TEXT ON ALL DROPDOWN ELEMENTS INCLUDING SELECTED VALUE */
    .custom-test-dropdown *,
    .custom-test-dropdown *:not(.svelte-select-list):not(.dropdown-menu):not(.options),
    .custom-test-dropdown .gradio-dropdown *,
    .custom-test-dropdown [data-testid="dropdown"] *,
    .custom-test-dropdown button *,
    .custom-test-dropdown span,
    .custom-test-dropdown div,
    .custom-test-dropdown p,
    .custom-test-dropdown .selected-item,
    .custom-test-dropdown .current-value,
    .custom-test-dropdown .display-value {
        color: white !important;
        background-color: transparent !important;
    }
    
    /* HIDE LABEL */
    .custom-test-dropdown label,
    .custom-test-dropdown .wrap > label {
        display: none !important;
    }
    
    /* FOCUS STATES */
    .custom-test-dropdown .gradio-dropdown:focus,
    .custom-test-dropdown [data-testid="dropdown"]:focus,
    .custom-test-dropdown .wrap:focus-within,
    .custom-test-dropdown button:focus,
    .custom-test-dropdown select:focus {
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3), 0 4px 12px rgba(72, 131, 255, 0.4) !important;
    }    /* DROPDOWN MENU CONTAINER - TARGET ALL POSSIBLE MENU SELECTORS */
    .custom-test-dropdown .gradio-dropdown + div,
    .custom-test-dropdown [data-testid="dropdown"] + div,
    .custom-test-dropdown .dropdown-content,
    .custom-test-dropdown .dropdown-menu,
    .custom-test-dropdown .options,
    .custom-test-dropdown .svelte-select-list,
    .custom-test-dropdown [role="listbox"],
    .custom-test-dropdown ul,
    .custom-test-dropdown .menu,
    .custom-test-dropdown div[class*="dropdown"],
    .custom-test-dropdown div[class*="options"],
    .custom-test-dropdown div[class*="menu"] {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
    }
      /* DROPDOWN MENU ITEMS HOVER STATES */
    .custom-test-dropdown .gradio-dropdown + div:hover,
    .custom-test-dropdown [data-testid="dropdown"] + div:hover,
    .custom-test-dropdown .dropdown-content:hover,
    .custom-test-dropdown .dropdown-menu:hover,
    .custom-test-dropdown .options:hover,
    .custom-test-dropdown .svelte-select-list:hover,
    .custom-test-dropdown [role="listbox"]:hover,
    .custom-test-dropdown ul:hover,
    .custom-test-dropdown .menu:hover,
    .custom-test-dropdown div[class*="dropdown"]:hover,
    .custom-test-dropdown div[class*="options"]:hover,
    .custom-test-dropdown div[class*="menu"]:hover,
    .custom-test-dropdown .gradio-dropdown + div li:hover,
    .custom-test-dropdown [data-testid="dropdown"] + div li:hover,
    .custom-test-dropdown .dropdown-content li:hover,
    .custom-test-dropdown .dropdown-menu li:hover,
    .custom-test-dropdown .options li:hover,
    .custom-test-dropdown .svelte-select-list li:hover,
    .custom-test-dropdown [role="listbox"] li:hover,
    .custom-test-dropdown ul li:hover,
    .custom-test-dropdown .menu li:hover {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
    }
      /* DROPDOWN BUTTON ONLY - #4883FF - MAXIMUM SPECIFICITY */
    .custom-test-dropdown button,
    .custom-test-dropdown .gradio-dropdown button,
    .custom-test-dropdown [data-testid="dropdown"] button,
    .custom-test-dropdown .svelte-select button,
    .custom-test-dropdown .wrap button,
    .custom-test-dropdown button[type="button"],
    .custom-test-dropdown input[type="button"],
    .custom-test-dropdown select,
    .custom-test-dropdown .gradio-dropdown,
    .custom-test-dropdown [data-testid="dropdown"]:not([data-testid="dropdown"] + div),
    .custom-test-dropdown .svelte-select:not(.svelte-select-list) {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
        border: none !important;
    }
      /* DROPDOWN HOVER STATES - MAINTAIN SAME BLUE COLOR */
    .custom-test-dropdown button:hover,
    .custom-test-dropdown .gradio-dropdown button:hover,
    .custom-test-dropdown [data-testid="dropdown"] button:hover,
    .custom-test-dropdown .svelte-select button:hover,
    .custom-test-dropdown .wrap button:hover,
    .custom-test-dropdown button[type="button"]:hover,
    .custom-test-dropdown input[type="button"]:hover,
    .custom-test-dropdown select:hover,
    .custom-test-dropdown .gradio-dropdown:hover,
    .custom-test-dropdown [data-testid="dropdown"]:hover:not([data-testid="dropdown"] + div),
    .custom-test-dropdown .svelte-select:hover:not(.svelte-select-list) {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
        border: none !important;
        transform: none !important;
        box-shadow: 0 4px 12px rgba(72, 131, 255, 0.3) !important;
    }
    /* CLEAN UP - REMOVE ALL CONFLICTING RULES */    /* OVERRIDE ANY POTENTIAL BLACK/DARK BACKGROUNDS ON HOVER */
    .custom-test-dropdown *:hover {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
    }
    
    /* NUCLEAR OPTION: FORCE WHITE TEXT ON SELECTED OPTION */
    .custom-test-dropdown [class],
    .custom-test-dropdown [class] *,
    .custom-test-dropdown .gradio-dropdown [class],
    .custom-test-dropdown .gradio-dropdown [class] *,
    .custom-test-dropdown [data-testid="dropdown"] [class],
    .custom-test-dropdown [data-testid="dropdown"] [class] *,
    .custom-test-dropdown button[class],
    .custom-test-dropdown button[class] *,
    .custom-test-dropdown div[style],
    .custom-test-dropdown span[style],
    .custom-test-dropdown div[style] *,
    .custom-test-dropdown span[style] * {
        color: white !important;
    }
      /* SPECIFIC OVERRIDE FOR CHART BUTTON STYLES THAT MIGHT INTERFERE */
    .custom-test-dropdown.chart-btn:hover,
    .custom-test-dropdown .chart-btn:hover {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
        border-color: #4883FF !important;
    }    /* PREVENT ANY DEFAULT HOVER STYLES FROM OVERRIDING */
    .custom-test-dropdown:hover,
    .custom-test-dropdown *:hover:not(svg):not(path) {
        background-color: #4883FF !important;
        background: #4883FF !important;
        color: white !important;
    }
    
    /* ULTIMATE OVERRIDE FOR INLINE STYLES - MAXIMUM SPECIFICITY */
    .custom-test-dropdown[style*="color"] *,
    .custom-test-dropdown *[style*="color"],
    .custom-test-dropdown [style*="background"] *,
    .custom-test-dropdown *[style*="background"] {
        color: white !important;
        background-color: transparent !important;
    }
      /* FORCE WHITE TEXT ON BUTTON AND SELECTED CONTENT */
    .custom-test-dropdown button,
    .custom-test-dropdown button *,
    .custom-test-dropdown .gradio-dropdown button,
    .custom-test-dropdown .gradio-dropdown button *,
    .custom-test-dropdown [data-testid="dropdown"] button,
    .custom-test-dropdown [data-testid="dropdown"] button * {
        color: white !important;
        background: transparent !important;
    }
    
    /* ADDITIONAL SPECIFICITY FOR SELECTED VALUE TEXT */
    .custom-test-dropdown button span,
    .custom-test-dropdown .gradio-dropdown button span,
    .custom-test-dropdown [data-testid="dropdown"] button span,
    .custom-test-dropdown .selected-option,
    .custom-test-dropdown .current-option,
    .custom-test-dropdown .dropdown-value,
    .custom-test-dropdown [role="combobox"],
    .custom-test-dropdown [role="combobox"] *,
    .custom-test-dropdown [class*="value"],
    .custom-test-dropdown [class*="value"] *,
    .custom-test-dropdown [class*="selected"],
    .custom-test-dropdown [class*="selected"] * {
        color: white !important;
        background-color: transparent !important;
    }
    
    /* NO MORE UNIVERSAL OVERRIDES THAT COULD INTERFERE */
    """
