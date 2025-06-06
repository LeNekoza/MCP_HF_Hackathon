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
        title="Smart Hospital - Department Assistant",
        css=load_modern_hospital_css(),
        fill_height=True,
        head=load_latex_scripts(),
    ) as demo:
        
        # Main container with fixed layout
        with gr.Row(elem_classes="main-container", equal_height=True):
            
            # Left Sidebar - Chat Panel
            with gr.Column(scale=1, min_width=350, elem_classes="sidebar-container"):
                
                # Assistant Header - Compact
                gr.HTML("""
                <div class="assistant-header">
                    <div class="avatar-circle">👨‍⚕️</div>
                    <div class="assistant-text">
                        <h3>Medical Assistant</h3>
                        <p>How can I help you?</p>
                    </div>
                </div>
                """)
                
                # Model Selection in Chat Panel
                model_dropdown = gr.Dropdown(
                    label="Model",
                    choices=get_available_models(),
                    value=config.get("default_model", "nebius-llama-3.3-70b"),
                    container=True,
                    scale=1
                )
                
                # Chat Interface - Normal Chat
                chatbot = gr.Chatbot(
                    type="messages",
                    height=350,
                    show_copy_button=False,
                    show_share_button=False,
                    container=False
                )
                
                # Chat Input Area - Standard
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask about hospital status, patients, or medical queries...",
                        show_label=False,
                        lines=1,
                        max_lines=3,
                        container=False,
                        scale=4
                    )
                    send_btn = gr.Button("→", size="sm", scale=0, min_width=40)
            
            # Right Side - Dashboard
            with gr.Column(scale=2, elem_classes="dashboard-container"):
                
                # Dashboard Header - Clean without Model Selection
                with gr.Row(elem_classes="dashboard-header-row"):
                    with gr.Column(scale=2):
                        gr.HTML("""
                        <div class="dashboard-title">
                            <h1>SMART HOSPITAL</h1>
                            <p>Department Assistant</p>
                        </div>
                        """)
                    
                    with gr.Column(scale=1, elem_classes="dashboard-controls"):
                        # Quick Controls
                        status_btn = gr.Button(
                            "Hospital Status", 
                            elem_classes="header-action-btn",
                            size="sm",
                            scale=1
                        )
                
                # Navigation Buttons Row
                gr.HTML("""
                <div class="nav-buttons-container">
                    <button class="nav-btn active">Dashboard</button>
                    <button class="nav-btn">Forecasting</button>
                    <button class="nav-btn">Alerts</button>
                    <button class="nav-btn">Resources</button>
                </div>
                """)
                
                # Metrics Container - All 4 cards properly displayed
                gr.HTML("""
                <div class="metrics-container">
                    <!-- First Row: ICU Occupancy and Emergency Room Load -->
                    <div class="metrics-row">
                        <div class="metric-card">
                            <div class="progress-circle">
                                <svg width="120" height="120">
                                    <circle class="progress-circle-bg" cx="60" cy="60" r="54"></circle>
                                    <circle class="progress-circle-fill" cx="60" cy="60" r="54" 
                                            style="stroke-dasharray: 339.292; stroke-dashoffset: 98.195;"></circle>
                                </svg>
                                <div class="progress-text">71%</div>
                            </div>
                            <h3>ICU Occupancy</h3>
                            <p class="card-subtitle">(see citation) ▼</p>
                        </div>
                        
                        <div class="metric-card">
                            <svg class="load-chart" width="200" height="80">
                                <defs>
                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:0.3" />
                                        <stop offset="100%" style="stop-color:#3B82F6;stop-opacity:0.05" />
                                    </linearGradient>
                                </defs>
                                <path class="load-path" d="M 10 70 Q 30 50 50 45 T 90 40 T 130 35 T 170 30 T 190 25" 
                                      stroke="#3B82F6" stroke-width="3" fill="none"></path>
                                <path class="load-area" d="M 10 70 Q 30 50 50 45 T 90 40 T 130 35 T 170 30 T 190 25 L 190 70 L 10 70 Z" 
                                      fill="url(#gradient)"></path>
                            </svg>
                            <h3>Emergency Room Load</h3>
                        </div>
                    </div>
                    
                    <!-- Second Row: Staff Availability and Tool Usage -->
                    <div class="metrics-row">
                        <div class="metric-card">
                            <h3>Staff Availability</h3>
                            <div class="staff-metrics">
                                <div class="staff-item">
                                    <span class="staff-label">Doctors</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill doctors-progress"></div>
                                    </div>
                                    <span class="staff-percentage">75%</span>
                                </div>
                                <div class="staff-item">
                                    <span class="staff-label">Nurses</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill nurses-progress"></div>
                                    </div>
                                    <span class="staff-percentage">60%</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="usage-chart">
                                <div class="bar" style="height: 60%;"></div>
                                <div class="bar" style="height: 40%;"></div>
                                <div class="bar" style="height: 70%;"></div>
                                <div class="bar" style="height: 35%;"></div>
                                <div class="bar" style="height: 85%;"></div>
                            </div>
                            <h3>Tool Usage</h3>
                        </div>
                    </div>
                </div>
                """)
                
                # Advanced Settings - Collapsible
                with gr.Accordion("Advanced AI Settings", open=False, elem_classes="dashboard-settings"):
                    with gr.Row():
                        with gr.Column():
                            medical_specialty = gr.Dropdown(
                                label="Medical Specialty",
                                choices=[
                                    "General Medicine",
                                    "Cardiology", 
                                    "Neurology",
                                    "Orthopedics",
                                    "Psychiatry",
                                    "Emergency Medicine",
                                    "Pediatrics"
                                ],
                                value="General Medicine",
                                elem_classes="settings-dropdown",
                            )
                        
                        with gr.Column():
                            temperature = gr.Slider(
                                minimum=0.0,
                                maximum=2.0,
                                value=0.4,
                                step=0.1,
                                label="Temperature",
                                elem_classes="settings-slider",
                            )
                    
                    context_input = gr.Textbox(
                        label="Medical Context (Optional)",
                        placeholder="Patient symptoms, medical history, medications...",
                        lines=2,
                        elem_classes="context-input",
                    )
                    
                    max_tokens = gr.Slider(
                        minimum=100,
                        maximum=4000,
                        value=1000,
                        step=100,
                        label="Max Tokens",
                        elem_classes="settings-slider",
                        visible=False  # Hide to reduce clutter
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
            context: str
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
            context: str
        ):
            """Stream AI response for real-time effect"""
            if not message.strip():
                yield history, ""
                return

            # Add user message
            history.append({"role": "user", "content": message})
            yield history, ""
            
            # Check if this is a database query first
            try:
                from ..services.advanced_database_mcp import advanced_database_mcp
                
                # First check if it's a database-related query
                if any(keyword in message.lower() for keyword in [
                    'patient', 'room', 'nurse', 'doctor', 'staff', 'equipment', 
                    'medical', 'hospital', 'bed', 'top', 'list', 'statistics',
                    'occupancy', 'inventory', 'history', 'admission'
                ]):
                    # Process with advanced database capabilities
                    db_response = advanced_database_mcp.process_advanced_query(message)
                    
                    # If we got real data from the database, pass it through AI for analysis
                    if "Error processing" not in db_response and "Use more specific queries" not in db_response:
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
                        if model == "nebius-llama-3.3-70b" and nebius_model.is_available():
                            history.append({"role": "assistant", "content": ""})
                            
                            try:
                                response_generator = nebius_model.generate_response(
                                    prompt=enhanced_prompt,
                                    context=f"Database query results included in the analysis",
                                    specialty=specialty,
                                    max_tokens=max(max_tok, 2000),  # Ensure enough space for complete data + analysis
                                    temperature=temp,
                                    stream=True
                                )
                                
                                for chunk in response_generator:
                                    if chunk:
                                        history[-1]["content"] += chunk
                                        yield history, ""
                                        
                            except Exception as e:
                                error_msg = f"❌ Error analyzing database results: {str(e)}"
                                history[-1]["content"] = error_msg
                                yield history, ""
                        else:
                            # Fallback: use handle_ai_response for analysis
                            analyzed_response = handle_ai_response(enhanced_prompt, model, temp, max(max_tok, 2000), specialty, f"Database query results included in the analysis")
                            history.append({"role": "assistant", "content": ""})
                            
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
                # Stream response using Nebius
                history.append({"role": "assistant", "content": ""})
                
                try:
                    response_generator = nebius_model.generate_response(
                        prompt=message,
                        context=context if context.strip() else None,
                        specialty=specialty,
                        max_tokens=max_tok,
                        temperature=temp,
                        stream=True
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
                # Use fallback response (simulate streaming)
                response = handle_ai_response(message, model, temp, max_tok, specialty, context)
                history.append({"role": "assistant", "content": ""})
                
                # Stream the response word by word
                words = response.split()
                for i, word in enumerate(words):
                    if i == 0:
                        history[-1]["content"] = word
                    else:
                        history[-1]["content"] += " " + word
                    time.sleep(0.05)  # Simulate streaming delay
                    yield history, ""

        # Quick action handler
        def handle_status_update():
            return "Provide a comprehensive update on current hospital status", [
                {"role": "user", "content": "Provide a comprehensive update on current hospital status"}
            ]

        # Connect events
        msg.submit(
            fn=stream_response,
            inputs=[msg, chatbot, model_dropdown, temperature, max_tokens, medical_specialty, context_input],
            outputs=[chatbot, msg],
            show_progress="hidden",
        )

        send_btn.click(
            fn=stream_response,
            inputs=[msg, chatbot, model_dropdown, temperature, max_tokens, medical_specialty, context_input],
            outputs=[chatbot, msg],
            show_progress="hidden",
        )

        status_btn.click(
            fn=handle_status_update,
            outputs=[msg, chatbot],
        )

        # Load welcome message
        demo.load(
            fn=lambda: [
                {
                    "role": "assistant",
                    "content": "🏥 Welcome to Smart Hospital Assistant! I'm powered by advanced AI and connected to real hospital systems.\n\n**I can help you with:**\n• Hospital status and real-time metrics\n• Patient information and medical consultations\n• Staff scheduling and resource management\n• Medical equipment tracking\n• Emergency response coordination\n\nSelect your preferred AI model above and ask me anything!",
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
    context: str
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
            if "Error processing" not in db_response and "Use more specific queries" not in db_response:
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
                    analysis_max_tokens = max(max_tokens, 2000)  # Ensure enough space for complete data + analysis
                    
                response = nebius_model.generate_response(
                    prompt=user_message,
                    context=context if context.strip() else None,
                    specialty=specialty,
                    max_tokens=analysis_max_tokens,
                    temperature=temperature,
                    stream=False
                )
                # Apply LaTeX formatting to the response
                formatted_response = format_medical_response(response, specialty)
                return formatted_response + disclaimer
            else:
                return "❌ Nebius API is not available. Please check your API key configuration." + disclaimer
                
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
        medical_responses.append(f"Given the medical context you provided and your {specialty.lower()} question about '{user_message}', here's what I can tell you.")
    
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
        "mistral-7b"
    ]


def load_latex_scripts():
    """Load LaTeX rendering scripts for mathematical content"""
    return """
    <script src="static/js/latex-renderer.js"></script>
    <script src="static/js/app.js"></script>
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
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
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
    .sidebar-container [class*="dropdown"]:not([class*="chatbot"]) *,
    .sidebar-container [class*="select"]:not([class*="chatbot"]) * {
        background: #3b82f6 !important;
        background-color: #3b82f6 !important;
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
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    /* Dashboard Header with Model Selection */
    .dashboard-header-row {
        background: white !important;
        padding: 20px 32px !important;
        border-bottom: 1px solid #e2e8f0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 20px !important;
        flex-shrink: 0 !important;
    }
    
    .dashboard-title h1 {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.5px !important;
        margin: 0 0 2px 0 !important;
    }
    
    .dashboard-title p {
        font-size: 14px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    
    /* Header Controls - Model Selection */
    .dashboard-controls {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
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
        padding: 12px 32px !important;
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
    """
