"""
Main Gradio Interface Components - ChatGPT-like Interface
"""

import asyncio
import time
from typing import Any, Dict, List

import gradio as gr

from ..models.mcp_handler import MCPHandler
from ..models.nebius_model import NebiusModel
from ..utils.helpers import process_user_input


def create_main_interface(config: Dict[str, Any]) -> gr.Blocks:
    """
    Create a ChatGPT-like Gradio interface for the MCP HF Hackathon application

    Args:
        config: Configuration dictionary

    Returns:
        gr.Blocks: The ChatGPT-style Gradio interface"""
    # Initialize MCP handler and Nebius model
    mcp_handler = MCPHandler(config)
    nebius_model = NebiusModel()

    with gr.Blocks(
        title="Hospital AI Helper - Medical Assistant",
        css=load_chatgpt_css(),
        fill_height=True,
    ) as demo:  # Header with title and model selection
        with gr.Row(elem_classes="header-row"):
            with gr.Column(scale=1, min_width=200):
                gr.Markdown(
                    """
<<<<<<< Updated upstream
                    # 🏥 Hospital AI Helper
                    *Powered by MCP & Nebius Studio*
=======
                    # 🤖 MCP AIs Assistant
                    *Powered by Model Context Protocol*
>>>>>>> Stashed changes
                    """,
                    elem_classes="header-title",
                )
            with gr.Column(scale=1, min_width=150):
                model_dropdown = gr.Dropdown(
                    label="AI Model",
                    choices=get_available_models(),
                    value=config.get("default_model", "nebius-llama-3.3-70b"),
                    elem_classes="model-selector",
                    scale=1,
                )

        # Main chat interface
        chatbot = gr.Chatbot(
            type="messages",
            height=400,
            bubble_full_width=False,
            show_copy_button=True,
            show_share_button=False,
            avatar_images=(
                "./static/images/user-avatar.svg",
                "./static/images/bot-avatar.svg",
            ),
            elem_classes="main-chatbot",
        )  # Chat input area with improved styling
        with gr.Row(elem_classes="input-row"):
            with gr.Column(scale=1, min_width=200):
                msg = gr.Textbox(
                    placeholder="Ask about medical symptoms, health questions, or general assistance...",
                    show_label=False,
                    lines=1,
                    max_lines=8,
                    elem_classes="chat-input",
                    container=False,
                )
            with gr.Column(scale=0, min_width=50):
                send_btn = gr.Button(
                    "➤", variant="primary", elem_classes="send-button", size="sm"
                )

        # Action buttons
        with gr.Row(elem_classes="action-row"):
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
            with gr.Column():
                gr.Markdown("", elem_classes="spacer")  # Spacer
            settings_btn = gr.Button("⚙️ Settings", variant="secondary", size="sm")

        # Medical specialty selector
        with gr.Row(elem_classes="specialty-row"):
            medical_specialty = gr.Dropdown(
                label="Medical Specialty",
                choices=[
                    "General Medicine",
                    "Cardiology",
                    "Neurology",
                    "Orthopedics", 
                    "Psychiatry",
                    "Gastroenterology",
                    "Pulmonology",
                    "Endocrinology",
                    "Emergency Medicine",
                    "Pediatrics"
                ],
                value="General Medicine",
                elem_classes="specialty-selector",
                scale=1,
            )
            context_input = gr.Textbox(
                label="Medical Context (Optional)",
                placeholder="Medical history, symptoms, medications, etc...",
                lines=2,
                max_lines=4,
                elem_classes="context-input",
                scale=2,
            )

        # Collapsible settings panel
        with gr.Accordion(
            "Advanced Settings", open=False, elem_classes="settings-panel"
        ):
            with gr.Row():
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.4,  # Lower default for medical accuracy
                    step=0.1,
                    label="Temperature",
                    elem_classes="setting-slider",
                )
                max_tokens = gr.Slider(
                    minimum=100,
                    maximum=4000,
                    value=1000,
                    step=100,
                    label="Max Tokens",
                    elem_classes="setting-slider",
                )

        # Status indicator
        status = gr.Textbox(
            value="Ready",
            show_label=False,
            interactive=False,
            elem_classes="status-indicator",
        )

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
            return [], "", ""  # Clear message and context too

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
                from ..services.database_mcp import database_mcp
                
                if database_mcp.is_database_query(message):
                    # Process database query
                    db_response = database_mcp.process_user_query(message)
                    
                    # If we got real data from the database, use it
                    if "I couldn't find any matching information" not in db_response and "error" not in db_response.lower():
                        # Stream the database response
                        full_response = db_response + "\n\n*Data retrieved from hospital database*"
                        history.append({"role": "assistant", "content": ""})
                        
                        # Stream the response word by word
                        words = full_response.split()
                        for i, word in enumerate(words):
                            if i == 0:
                                history[-1]["content"] = word
                            else:
                                history[-1]["content"] += " " + word
                            time.sleep(0.02)  # Fast streaming for database results
                            yield history, ""
                        return
                        
            except Exception as e:
                # If database integration fails, continue with regular AI response
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

        clear_btn.click(fn=clear_conversation, outputs=[chatbot, msg, context_input])

        # Add some example conversations on load
        demo.load(
            fn=lambda: [
                {
                    "role": "assistant",
                    "content": "🏥 Hello! I'm your Hospital AI Helper powered by Nebius Studio and the Llama 3.3 70B model.\n\nI can help you with:\n• Medical consultations and symptom analysis\n• Health-related questions and advice\n• Medical information and explanations\n• General healthcare guidance\n\nPlease select a medical specialty above and describe your symptoms or questions. Remember: I provide information for educational purposes only and cannot replace professional medical advice.",
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
    Handle AI response generation with model routing

    Args:
        user_message: User's input message
        model: Selected model name
        temperature: Temperature setting
        max_tokens: Maximum tokens
        specialty: Medical specialty
        context: Medical context

    Returns:
        AI response string
    """
    # Medical disclaimer
    disclaimer = "\n\n⚠️ **Medical Disclaimer**: This is for informational purposes only and should not replace professional medical advice. Please consult with a healthcare provider for medical concerns."
    
    # First, check if this is a database query
    try:
        from ..services.database_mcp import database_mcp
        
        if database_mcp.is_database_query(user_message):
            # Process database query
            db_response = database_mcp.process_user_query(user_message)
            
            # If we got real data from the database, use it
            if "I couldn't find any matching information" not in db_response and "error" not in db_response.lower():
                return db_response + "\n\n*Data retrieved from hospital database*" + disclaimer
            
    except Exception as e:
        # If database integration fails, continue with regular AI response
        pass
    
    if model == "nebius-llama-3.3-70b":
        # Try to use Nebius model first
        try:
            from ..models.nebius_model import NebiusModel
            nebius_model = NebiusModel()
            
            if nebius_model.is_available():
                response = nebius_model.generate_response(
                    prompt=user_message,
                    context=context if context.strip() else None,
                    specialty=specialty,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False
                )
                return response + disclaimer
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
    
    return (
        base_response
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


def load_chatgpt_css():
    """Load ChatGPT-style CSS for the interface"""
    return """    /* Main container styling */
    .gradio-container {
        max-width: 100vw !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 0 !important;
        background: #ffffff !important;
        max-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        overflow-y: scroll !important;
    }
    
    /* Ensure full height usage */
    .gradio-container > div {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    /* Header styling - Medical theme */
    .header-row {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 20px 30px;
        margin-bottom: 0;
        border-radius: 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .header-title {
        margin: 0 !important;
    }
    
    .header-title h1 {
        margin: 0 !important;
        font-size: 1.8em !important;
        font-weight: 600 !important;
        color: white !important;
    }
    
    .model-selector {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Main chatbot styling - clean ChatGPT style */
    .main-chatbot {
        border: none !important;
        border-radius: 0 !important;
        height: 600px !important;
        background: #ffffff !important;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05) !important;
        width: 100% !important; 
        position: relative !important;
    }
      /* Input area styling - ChatGPT bottom input */
    .input-row {
        padding: 20px !important;
        background: #ffffff !important;
        border-top: 1px solid #e5e5e5 !important;
        margin: 0 !important;
        position: sticky !important;
        bottom: 0 !important;
        z-index: 100 !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05) !important;
        display: flex !important;
        align-items: flex-end !important;
        gap: 12px !important;
    }
      .chat-input {
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 0 rgba(16, 163, 127, 0) !important;
        transition: all 0.2s ease !important;
        resize: none !important;
        flex: 1 !important;
        min-height: 44px !important;
        max-height: 200px !important;
        overflow-y: auto !important;
        line-height: 1.5 !important;
    }
    
    .chat-input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        outline: none !important;
    }
    
    /* Medical specialty row styling */
    .specialty-row {
        padding: 15px 20px !important;
        background: #f8fafc !important;
        border-bottom: 1px solid #e2e8f0 !important;
        gap: 15px !important;
    }
    
    .specialty-selector {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        background: white !important;
    }
    
    .context-input {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        background: white !important;
        resize: vertical !important;
    }
    
    .context-input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        outline: none !important;
    }
    
      .send-button {
        background: #2563eb !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        color: white !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        min-width: 44px !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
    }
    
    .send-button:hover {
        background: #1d4ed8 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    .send-button:disabled {
        background: #d1d5db !important;
        cursor: not-allowed !important;
    }
    
    /* Action buttons styling */
    .action-row {
        padding: 10px 20px !important;
        background: #f9fafb !important;
        border-top: 1px solid #e5e5e5 !important;
        justify-content: space-between !important;
    }
    
    /* Settings panel - hidden by default like ChatGPT */
    .settings-panel {
        margin: 0 !important;
        border: none !important;
        border-top: 1px solid #e5e5e5 !important;
        border-radius: 0 !important;
        background: #f9fafb !important;
    }
    
    .setting-slider {
        margin: 10px 0 !important;
    }
    
    /* Status indicator - minimal like ChatGPT */
    .status-indicator {
        display: none !important;
    }
    
    /* Message styling - ChatGPT style bubbles */
    .message.user {
        background: #f7f7f8 !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        max-width: 80% !important;
        min-width: 150px !important;
        margin-left: auto !important;
    }
    /* Dark mode user message */
    .message.user.dark {
        background: #2d2d2d !important;
        border-color: #444 !important;
        color: #f0f0f0 !important;
        box-shadow: none !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        margin-left: auto !important;
    }
    
    .message.bot {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        max-width: 100% !important;
    }
    
    /* Chat message styling */
    .chatbot .message-wrap {
        padding: 16px 24px !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }
    
    .chatbot .message-wrap:last-child {
        border-bottom: none !important;
    }
    
    /* User message styling */
    .chatbot .user-message {
        background: #f7f7f8 !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin-left: auto !important;
        max-width: 70% !important;
        display: inline-block !important;
    }
    
    /* Assistant message styling */
    .chatbot .assistant-message {
        background: transparent !important;
        padding: 12px 0 !important;
        max-width: 100% !important;
    }
    
    /* Improved button styling */
    button {
        transition: all 0.2s ease !important;
        border-radius: 6px !important;
    }
    
    button:hover {
        transform: none !important;
        opacity: 0.9 !important;
    }
      /* Responsive design */
    @media (max-width: 768px) {
        .gradio-container {
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .header-row {
            padding: 15px 20px !important;
            flex-direction: column !important;
            gap: 15px !important;
        }
        
        .header-title h1 {
            font-size: 1.5em !important;
        }
        
        .model-selector {
            width: 100% !important;
        }
        
        .main-chatbot {
            height: calc(100vh - 280px) !important;
            border-radius: 0 !important;
        }
        
        .input-row {
            padding: 15px !important;
            flex-direction: column !important;
            gap: 10px !important;
        }
        
        .chat-input {
            font-size: 16px !important;
            width: 100% !important;
            min-height: 44px !important;
        }
        
        .send-button {
            width: 100% !important;
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        .action-row {
            padding: 10px 15px !important;
            flex-wrap: wrap !important;
            gap: 10px !important;
        }
        
        .settings-panel {
            margin: 0 !important;
        }
        
        .setting-slider {
            margin: 15px 0 !important;
        }
    }
    
    /* Tablet responsive design */
    @media (min-width: 769px) and (max-width: 1024px) {
        .gradio-container {
            max-width: 95% !important;
            padding: 0 10px !important;
        }
        
        .header-row {
            padding: 20px 25px !important;
        }
        
        .main-chatbot {
            height: calc(100vh - 250px) !important;
        }
        
        .input-row {
            padding: 18px !important;
        }
        
        .chat-input {
            font-size: 15px !important;
        }
    }
    
    /* Large screen optimization */
    @media (min-width: 1400px) {
        .gradio-container {
            max-width: 1400px !important;
        }
        
        .main-chatbot {
            height: 700px !important;
        }
        
        .chat-input {
            font-size: 17px !important;
        }
    }
    
    /* Touch device optimizations */
    @media (hover: none) and (pointer: coarse) {
        .chat-input {
            font-size: 16px !important;
            min-height: 44px !important;
            padding: 15px 18px !important;
        }
        
        .send-button {
            min-height: 48px !important;
            min-width: 48px !important;
            font-size: 20px !important;
        }
        
        button {
            min-height: 44px !important;
            padding: 12px 16px !important;
        }
        
        .setting-slider {
            margin: 20px 0 !important;
        }
    }
    
    /* Landscape mobile optimization */
    @media (max-width: 768px) and (orientation: landscape) {
        .main-chatbot {
            height: calc(100vh - 200px) !important;
        }
        
        .header-row {
            padding: 10px 15px !important;
        }
        
        .header-title h1 {
            font-size: 1.3em !important;
        }
        
        .input-row {
            padding: 10px !important;
        }
    }
    
    /* Small mobile devices */
    @media (max-width: 480px) {
        .header-row {
            padding: 12px 15px !important;
        }
        
        .header-title h1 {
            font-size: 1.4em !important;
        }
        
        .main-chatbot {
            height: calc(100vh - 300px) !important;
        }
        
        .input-row {
            padding: 12px !important;
        }
        
        .action-row {
            padding: 8px 12px !important;
        }
        
        .chatbot .message-wrap {
            padding: 12px 16px !important;
        }
        
        .chatbot .user-message {
            max-width: 85% !important;
            padding: 10px 14px !important;
        }
    }
      /* Flexible grid system for settings */
    .settings-panel .gradio-row {
        flex-wrap: wrap !important;
        gap: 15px !important;
    }
    
    @media (max-width: 768px) {
        .settings-panel .gradio-row {
            flex-direction: column !important;
        }
        
        .settings-panel .gradio-column {
            width: 100% !important;
            min-width: unset !important;
        }
    }
    
    /* Improved focus states for accessibility */
    .chat-input:focus,
    .send-button:focus,
    .model-selector:focus,
    .specialty-selector:focus,
    .context-input:focus {
        outline: 2px solid #2563eb !important;
        outline-offset: 2px !important;
    }
    
    /* Better button states */
    .send-button:active {
        transform: scale(0.98) !important;
    }
    
    /* Smooth transitions for responsive changes */
    .gradio-container,
    .header-row,
    .main-chatbot,
    .input-row {
        transition: all 0.3s ease !important;
    }
    
    /* Loading states */
    .chatbot.loading {
        opacity: 0.7 !important;
    }
    
    .chatbot.loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid #2563eb;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
    
    /* High DPI display optimization */
    @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
        .chat-input,
        .send-button {
            border-width: 0.5px !important;
        }
    }
    
    /* Dark mode support (optional) */
    @media (prefers-color-scheme: dark) {
        .gradio-container {
            background: #1a1a1a !important;
            color: white !important;
        }
        
        .main-chatbot {
            background: #2d2d2d !important;
        }
        
        .chat-input {
            background: #3a3a3a !important;
            border-color: #555 !important;
            color: white !important;
        }
        
        .input-row {
            background: #2d2d2d !important;
            border-color: #555 !important;
        }
    }
    
    /* Animation for message loading */
    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message {
        animation: messageSlideIn 0.3s ease-out !important;
    }
    
    /* Hide Gradio branding */
    .footer {
        display: none !important;
    }
    
    .gr-button-secondary {
        background: transparent !important;
        border: 1px solid #d1d5db !important;
        color: #374151 !important;
    }
    
    .gr-button-secondary:hover {
        background: #f9fafb !important;
        border-color: #9ca3af !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    """
