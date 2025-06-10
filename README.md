---
title: Hospital AI Helper Aid
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
license: mit
tags:
  - mcp-server-track
  - agent-demo-track
---

# Hospital AI Helper Aid (H.A.H.A)

## 🚀 Overview

The Hospital AI Helper Aid (H.A.H.A) is an advanced AI-powered application designed to assist medical professionals and patients within a hospital environment. It features a sophisticated chat interface for medical consultations, real-time access to hospital data through database integration, and an interactive dashboard for visualizing key hospital metrics. The system leverages the Model Context Protocol (MCP) for intelligent data handling and integrates with powerful large language models like Nebius Llama 3.3 70B.

The main interface and application logic are orchestrated within [`src/components/interface.py`](src/components/interface.py).

## ✨ Features

*   **AI-Powered Medical Consultations:** Provides medical information, guidance, and advice through an intelligent chat interface.
*   **Real-time Database Integration:** Connects to a hospital database (Neon PostgreSQL) to fetch and display live data on patients, rooms, staff, and inventory. This is primarily handled by `src/services/advanced_database_mcp.py` (as referenced in [`docs/project/AI_DATABASE_INTEGRATION_FLOW.md`](docs/project/AI_DATABASE_INTEGRATION_FLOW.md)) and integrated into the chat flow in [`src/components/interface.py`](src/components/interface.py).
*   **Interactive Dashboard:** A modern, responsive dashboard built with Gradio, showcasing vital hospital statistics and data visualizations.
*   **Natural Language Queries:** Users can query the database using plain English; the system fetches relevant data which is then analyzed by the AI.
*   **AI-Enhanced Data Analysis:** Database results are processed by the AI to provide contextual insights, summaries, and professional formatting, as seen in the `stream_response` function within [`src/components/interface.py`](src/components/interface.py).
*   **LaTeX Formatting:** Medical values (e.g., blood pressure, BMI, dosages) are rendered using LaTeX for clarity and professionalism, facilitated by [`src/utils/latex_formatter.py`](src/utils/latex_formatter.py).
*   **Streaming Responses & Loading Indicators:** Enhanced user experience with real-time streaming of AI responses and dynamic loading indicators (e.g., "🤔 Thinking...", "🗄️ Querying the database...") during processing, implemented in the `stream_response` function in [`src/components/interface.py`](src/components/interface.py).
*   **Contextual Chat History:** Maintains conversation context for seamless interactions, managed within the Gradio interface logic.
*   **Secure Configuration:** Manages sensitive credentials securely using environment variables (`.env`).

## 🛠️ Tech Stack

*   **Backend:** Python
*   **Web Interface:** Gradio
*   **AI Model Provider:** Nebius (specifically `meta-llama/Llama-3.3-70B-Instruct`)
*   **Database:** PostgreSQL (Neon)
*   **Core Logic:** Model Context Protocol (MCP) integration, custom AI model handlers.
*   **Styling:** Custom CSS for a modern hospital theme.

## 📦 MCP Tools/Servers

**🏷️ Track 1: MCP Server / Tool**

This project implements a **Model Context Protocol (MCP) Database Integration** to enable the AI assistant to interact with a live hospital database.
*   **Core Engine:** The integration involves components like [`src/models/mcp_handler.py`](src/models/mcp_handler.py) and `src/services/advanced_database_mcp.py`.
    *   **Intent Recognition:** The system parses user queries to determine if they relate to database information (e.g., patient lookup, room status).
    *   **Data Retrieval & AI Analysis:** Instead of directly generating SQL and returning raw data, the system fetches data based on the user's intent. This data is then passed to the AI model along with the original user query. The AI analyzes the data, provides insights, and formats the response professionally. This flow is detailed in [`docs/project/AI_DATABASE_INTEGRATION_FLOW.md`](docs/project/AI_DATABASE_INTEGRATION_FLOW.md) and implemented in the `stream_response` and [`handle_ai_response`](src/components/interface.py) functions within [`src/components/interface.py`](src/components/interface.py).
*   **Seamless Chatbot Integration:** The main interface in [`src/components/interface.py`](src/components/interface.py) automatically detects if a user's query should involve database interaction, fetches data, and then uses the AI to present a comprehensive, analyzed response.

## 🎨 Custom Gradio Components

The user interface is built using Gradio, with several custom components and layouts defined primarily in [`src/components/interface.py`](src/components/interface.py):
*   **Main Dashboard (`gr.Blocks`):** The entire application is structured within `gr.Blocks`, using `gr.Row`, `gr.Column`, and `gr.HTML` to create a bespoke layout.
*   **Custom HTML Sections:**
    *   **Headers & Navigation:** Includes an assistant header, dashboard title, controls (like a "Helpline" button), and navigation buttons ("Dashboard", "Data") created using `gr.HTML`.
    *   **Dashboard & Data Views:** Specific sections like `#dashboard-section` and `#data-section` (with tabs for Patients, Staff, Rooms) are rendered using `gr.HTML`, allowing for custom styling and structure beyond standard Gradio components.
*   **Styled Chat Interface (`gr.Chatbot`):** The chatbot is configured with specific properties (`type="messages"`, `layout="bubble"`) and custom CSS for appearance.
*   **Dynamic Loading Indicators:** Implemented within the `stream_response` function in [`src/components/interface.py`](src/components/interface.py). These are HTML snippets injected into the chat history to show messages like "🤔 Thinking...", "🗄️ Querying the database...", providing real-time feedback.
*   **CSS Styling:** Extensive custom CSS is loaded via the [`load_modern_hospital_css`](src/components/interface.py) function (which reads from [`static/css/styles.css`](static/css/styles.css)) to achieve a unique "modern hospital" theme, overriding default Gradio styles.

## 📡 MCP Server Configuration

This project provides a Model Context Protocol (MCP) server configured for seamless integration and communication with clients supporting Server-Sent Events (SSE) and standard input/output (stdio).

### 🔗 MCP Server URL

```
http://localhost:7860/gradio_api/mcp/sse
```

### 🧰 Available MCP Tools

* **stream\_response\_with\_state**
  Streams AI-generated responses, updating the relevant chat states.

* **stream\_response\_with\_state\_**
  Variant streaming response handler with state management.

* **handle\_helpline\_with\_state**
  Manages helpline interactions, maintaining the conversation state throughout.

* **handle\_tool\_selection**
  Facilitates the selection and handling of tools via dropdown, managing separate chat flows.

* **\<lambda>**
  Delivers a welcoming assistant message introducing the system's capabilities, including medical guidance, hospital support, health monitoring, and emergency assistance.

### 🎥 MCP Server Demo Video

[Link to MCP Server Demo Video - Coming Soon]
> Video demonstration showing the MCP server integration with Claude Desktop/Cursor, showcasing real-time hospital data queries and AI-powered medical consultations.

### 🛠️ Integration Instructions

To integrate this MCP server with SSE-compatible clients (e.g., Cursor, Windsurf, Cline), add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "gradio": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

### 🧪 Experimental stdio Support

For clients limited to standard input/output protocols, first ensure Node.js is installed, then integrate using:

```json
{
  "mcpServers": {
    "gradio": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:7860/gradio_api/mcp/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}
```

This setup ensures broader compatibility and flexibility across various client types and integration scenarios.

## 🤖 AI Agent

The primary AI agent powering the medical assistant is the **`meta-llama/Llama-3.3-70B-Instruct`** model, accessed via the Nebius API.
*   **Integration:** Managed through the [`NebiusModel`](src/models/nebius_model.py) class, which is initialized and used in [`src/components/interface.py`](src/components/interface.py). Details of this integration can also be found in [`docs/setup/NEBIUS_INTEGRATION.md`](docs/setup/NEBIUS_INTEGRATION.md).
*   **Capabilities:**
    *   **Medical Consultation:** Answers health-related questions and provides medical information.
    *   **Chat Completion:** Engages in natural conversations, maintaining context.
    *   **Data Analysis & Presentation:** When provided with data from the hospital database (via the `stream_response` logic in [`src/components/interface.py`](src/components/interface.py)), the AI analyzes this information in conjunction with the user's query. It then generates a comprehensive response including structured data, medical analysis, LaTeX formatting, and recommendations. This process is outlined in the `enhanced_prompt` logic within `stream_response` and [`handle_ai_response`](src/components/interface.py).
    *   **Streaming Responses:** Supports streaming of responses for an interactive user experience.
*   **Configuration:** Model parameters like temperature and max tokens are handled within the AI interaction functions in [`src/components/interface.py`](src/components/interface.py).

## 🤖 Agentic Demo

**🏷️ Track 3: Agentic Demo**

H.A.H.A represents a complete agentic application that showcases the power of AI agents in healthcare environments. The system demonstrates:

- **Intelligent Medical Consultation Agent**: Provides contextual medical advice and information
- **Database Query Agent**: Translates natural language queries into structured database operations
- **Data Analysis Agent**: Processes hospital data to provide insights and recommendations
- **Multi-modal Interaction**: Seamlessly integrates chat, dashboard visualization, and real-time data

### 🎥 Application Demo Video

[Link to Application Overview Video - Coming Soon]
> Comprehensive video walkthrough demonstrating the hospital AI assistant's capabilities, including medical consultations, database queries, dashboard interactions, and real-time data analysis.

### 🏥 Use Cases Demonstrated

1. **Patient Information Lookup**: Natural language queries for patient records and medical history
2. **Room Management**: Real-time room occupancy and availability tracking
3. **Staff Coordination**: Staff scheduling and availability management
4. **Medical Consultation**: AI-powered medical guidance and information
5. **Emergency Response**: Quick access to critical hospital information during emergencies

## 📁 Project Structure

A brief overview of the project structure:
```
MCP_HF_Hackathon/
├── [`app.py`](app.py )                          # Main application entry point
├── [`dev_server.py`](dev_server.py )            # Development server
├── [`requirements.txt`](requirements.txt )      # Python dependencies
├── [`README.md`](README.md )                    # Readme file
├── src/                          # Source code
│   ├── components/               # UI components
│   │   └── [`src/components/interface.py`](src/components/interface.py )          # Main Gradio interface
│   ├── models/                   # AI Model handlers
│   │   ├── mcp_handler.py        # MCP protocol handler
│   │   └── nebius_model.py       # Nebius AI model wrapper
│   ├── services/                 # Business logic services
│   └── utils/                    # Utility functions
├── static/                       # Static assets (CSS, JS)
├── docs/                         # Project documentation
└── tests/                        # Test files
```
## ⚙️ Setup and Installation

1.  **Clone the repository.**
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\Activate.ps1
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    *   Copy `.env.template` to `.env`.
    *   Fill in your `NEBIUS_API_KEY` and Neon database credentials (e.g., `NEON_HOST`, `NEON_DATABASE`, `NEON_USER`, `NEON_PASSWORD`) in the `.env` file.

## ▶️ Running the Application

*   **Development Server (with auto-reload):**
    ```bash
    python dev_server.py
    ```
*   **Main Application:**
    ```bash
    python app.py
    ```
    Access the application by navigating to `http://localhost:7860` (or the port configured in [`.env`](.env)).

## 🗄️ Database

The application integrates with a Neon PostgreSQL database containing hospital data across tables like `users`, `patient_records`, `rooms`, `occupancy`, etc. (as detailed in [`README.md`](README.md) under Database Overview and [`docs/project/MCP_DATABASE_INTEGRATION.md`](docs/project/MCP_DATABASE_INTEGRATION.md)). This enables the AI to provide responses based on real-time information. Secure database configuration is handled via [`.env`](.env).

## 📡 MCP Server Configuration

This project provides a Model Context Protocol (MCP) server configured for seamless integration and communication with clients supporting Server-Sent Events (SSE) and standard input/output (stdio).

### 🔗 MCP Server URL

```
http://localhost:7860/gradio_api/mcp/sse
```

### 🧰 Available MCP Tools

* **stream\_response\_with\_state**
  Streams AI-generated responses, updating the relevant chat states.

* **stream\_response\_with\_state\_**
  Variant streaming response handler with state management.

* **handle\_helpline\_with\_state**
  Manages helpline interactions, maintaining the conversation state throughout.

* **handle\_tool\_selection**
  Facilitates the selection and handling of tools via dropdown, managing separate chat flows.

* **\<lambda>**
  Delivers a welcoming assistant message introducing the system's capabilities, including medical guidance, hospital support, health monitoring, and emergency assistance.

### 🛠️ Integration Instructions

To integrate this MCP server with SSE-compatible clients (e.g., Cursor, Windsurf, Cline), add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "gradio": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

### 🧪 Experimental stdio Support

For clients limited to standard input/output protocols, first ensure Node.js is installed, then integrate using:

```json
{
  "mcpServers": {
    "gradio": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:7860/gradio_api/mcp/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}
```

This setup ensures broader compatibility and flexibility across various client types and integration scenarios.




---

**Happy Hacking! 🚀**