"""
Main Gradio Interface Components
"""

import gradio as gr
from typing import Dict, Any
from ..models.mcp_handler import MCPHandler
from ..utils.helpers import process_user_input

def create_main_interface(config: Dict[str, Any]) -> gr.Blocks:
    """
    Create the main Gradio interface for the MCP HF Hackathon application
    
    Args:
        config: Configuration dictionary
        
    Returns:
        gr.Blocks: The main Gradio interface
    """
    
    # Initialize MCP handler
    mcp_handler = MCPHandler(config)
    
    with gr.Blocks(
        title="MCP HF Hackathon",
        theme=gr.themes.Soft(),
        css=load_custom_css()
    ) as demo:
        
        # Header
        with gr.Row():
            gr.Markdown(
                """
                # 🤖 MCP HF Hackathon
                ## Model Context Protocol Integration with Hugging Face
                
                Welcome to our innovative application that leverages the power of MCP 
                for enhanced AI model interactions.
                """
            )
        
        # Main content area
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                with gr.Group():
                    gr.Markdown("### Input")
                    user_input = gr.Textbox(
                        label="Your message",
                        placeholder="Enter your message here...",
                        lines=3
                    )
                    
                    # Model selection
                    model_dropdown = gr.Dropdown(
                        label="Select Model",
                        choices=get_available_models(),
                        value=config.get("default_model", "gpt-3.5-turbo")
                    )
                    
                    submit_btn = gr.Button("Submit", variant="primary")
                
                # Settings panel
                with gr.Accordion("Advanced Settings", open=False):
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="Temperature"
                    )
                    
                    max_tokens = gr.Slider(
                        minimum=1,
                        maximum=4000,
                        value=1000,
                        step=50,
                        label="Max Tokens"
                    )
            
            with gr.Column(scale=3):
                # Output section
                with gr.Group():
                    gr.Markdown("### Response")
                    output = gr.Textbox(
                        label="AI Response",
                        lines=15,
                        interactive=False
                    )
                
                # Status and logs
                with gr.Accordion("Status & Logs", open=False):
                    status = gr.Textbox(
                        label="Status",
                        value="Ready",
                        interactive=False
                    )
                    
                    logs = gr.Textbox(
                        label="Logs",
                        lines=5,
                        interactive=False
                    )
        
        # Example inputs
        with gr.Row():
            gr.Examples(
                examples=[
                    ["Hello! Can you help me understand MCP?"],
                    ["What are the benefits of using Hugging Face models?"],
                    ["Explain the concept of model context protocols"],
                ],
                inputs=user_input,
                label="Example Prompts"
            )
        
        # Event handlers
        submit_btn.click(
            fn=handle_user_input,
            inputs=[user_input, model_dropdown, temperature, max_tokens],
            outputs=[output, status, logs]
        )
        
        user_input.submit(
            fn=handle_user_input,
            inputs=[user_input, model_dropdown, temperature, max_tokens],
            outputs=[output, status, logs]
        )
    
    return demo

def handle_user_input(user_msg: str, model: str, temp: float, max_tok: int):
    """
    Handle user input and generate response
    
    Args:
        user_msg: User's input message
        model: Selected model name
        temp: Temperature setting
        max_tok: Maximum tokens
        
    Returns:
        Tuple of (response, status, logs)
    """
    try:
        # Process the input (placeholder for actual implementation)
        response = f"Echo: {user_msg} (Model: {model}, Temp: {temp}, Max Tokens: {max_tok})"
        status = "Success"
        logs = f"Processed message with {len(user_msg)} characters"
        
        return response, status, logs
        
    except Exception as e:
        return f"Error: {str(e)}", "Error", f"Error occurred: {str(e)}"

def get_available_models():
    """Get list of available models"""
    return [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-3-sonnet",
        "llama-2-7b",
        "mistral-7b"
    ]

def load_custom_css():
    """Load custom CSS for the interface"""
    return """
    .gradio-container {
        max-width: 1200px !important;
    }
    
    .group {
        border-radius: 10px;
        padding: 15px;
    }
    
    .submit-btn {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        border: none;
        color: white;
        font-weight: bold;
    }
    """
