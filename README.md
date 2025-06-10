---
title: Health AI Hospital Aid
emoji: 🏥
colorFrom: blue
colorTo: pink
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
license: mit
tags:
- mcp-server-track
- agent-demo-track
short_description: 🏥 AI assistant for hospital operations
---

# Health AI Hospital Aid (H.A.H.A)


## 🌟 Inspiration

The inspiration for H.A.H.A. stems from the COVID-19 pandemic, a time when hospitals across the globe faced overwhelming pressure and resource mismanagement. We remember vividly how many medical institutions struggled to allocate and monitor critical supplies like oxygen bags, beds, and staff in real time. This project is our response to that crisis — aiming to empower hospitals with intelligent, data-driven tools to streamline operations, enhance patient care, and ensure that vital resources are used efficiently during both everyday operations and emergencies.

## 🚀 Overview

The Health AI Hospital Aid (H.A.H.A) is an advanced AI-powered application designed to assist medical professionals and patients within a hospital environment. It features a sophisticated chat interface for medical consultations, real-time access to hospital data through database integration, and an interactive dashboard for visualizing key hospital metrics and forecast data. The system leverages the Model Context Protocol (MCP) for intelligent data handling and integrates with powerful large language models like Nebius Llama 3.3 70B.

The main interface and application logic are orchestrated within [`src/components/interface.py`](src/components/interface.py).

## ✨ Features

- **AI-Powered Medical Consultations:** Provides medical information, guidance, and advice through an intelligent chat interface.
- **Real-time Database Integration:** Connects to a hospital database (Neon PostgreSQL) to fetch and display live data on patients, rooms, staff, and inventory. This is primarily handled by `src/services/advanced_database_mcp.py` and integrated into the chat flow in [`src/components/interface.py`](src/components/interface.py).
- **Interactive Dashboard:** A modern, responsive dashboard built with Gradio, designed to showcase key hospital statistics and predictive analytics. Users can inquire about the dashboard content by tagging @analysis when asking questions.
- **Natural Language Queries:** Users can query the database using plain English; the system fetches relevant data which is then analyzed by the AI.
- **AI-Enhanced Data Analysis:** Database results are processed by the AI to provide contextual insights, summaries, and professional formatting, as seen in the `stream_response` function within [`src/components/interface.py`](src/components/interface.py).
- **LaTeX Formatting:** Medical values (e.g., blood pressure, BMI, dosages) are rendered using LaTeX for clarity and professionalism, facilitated by [`src/utils/latex_formatter.py`](src/utils/latex_formatter.py).
- **Streaming Responses & Loading Indicators:** Enhanced user experience with real-time streaming of AI responses and dynamic loading indicators (e.g., "🤔 Thinking...", "🗄️ Querying the database...") during processing, implemented in the `stream_response` function in [`src/components/interface.py`](src/components/interface.py).
- **Contextual Chat History:** Maintains conversation context for seamless interactions, managed within the Gradio interface logic.
- **Secure Configuration:** Manages sensitive credentials securely using environment variables (`.env`).

## 🛠️ Tech Stack

- **Backend:** Python
- **Web Interface:** Gradio
- **AI Model Provider:** Nebius (specifically `meta-llama/Llama-3.3-70B-Instruct`)
- **Database:** PostgreSQL (Neon)
- **Core Logic:** Model Context Protocol (MCP) integration, custom AI model handlers.
- **Styling:** Custom CSS for a modern hospital theme.



### 🎥 Track 1 Demo Video

[https://drive.google.com/file/d/1q-aYIFUFP7zCNOGNUB8_RjZFIYxpNtql/view?usp=sharing]


### 🎥 Track 3 Demo Video

[https://drive.google.com/file/d/1M9hF_KJwsNEjAUzL9v2gjQ8e1LlW4V87/view?usp=sharing]

> Comprehensive video walkthrough demonstrating the hospital AI assistant's capabilities, including medical consultations, database queries, dashboard interactions, and real-time data analysis.

## 📦 MCP Tools/Servers

**🏷️ Track 1: MCP Server / Tool**

This project implements a **Model Context Protocol (MCP) Database Integration** to enable the AI assistant to interact with a live hospital database.

- **Core Engine:** The integration involves components like [`src/models/mcp_handler.py`](src/models/mcp_handler.py) and `src/services/advanced_database_mcp.py`.
  - **Intent Recognition:** The system parses user queries to determine if they relate to database information (e.g., patient lookup, room status).
  - **Data Retrieval & AI Analysis:** Instead of directly generating SQL and returning raw data, the system fetches data based on the user's intent. This data is then passed to the AI model along with the original user query. The AI analyzes the data, provides insights, and formats the response professionally. This flow is implemented in the `stream_response` and [`handle_ai_response`](src/components/interface.py) functions within [`src/components/interface.py`](src/components/interface.py).
- **Seamless Chatbot Integration:** The main interface in [`src/components/interface.py`](src/components/interface.py) automatically detects if a user's query should involve database interaction, fetches data, and then uses the AI to present a comprehensive, analyzed response.

## 📡 MCP Server Configuration

This project provides a Model Context Protocol (MCP) server configured for seamless integration and communication with clients supporting Server-Sent Events (SSE) and standard input/output (stdio).

### 🔗 MCP Server URL

```
https://agents-mcp-hackathon-health-ai-hospital-aid.hf.space/gradio_api/mcp/sse
```

Visit below link on how to use MCP tools
```
https://agents-mcp-hackathon-health-ai-hospital-aid.hf.space/?view=api
```

### 🧰 Available MCP Tools

- **health_ai_hospital_aid_stream_response_with_state**
  Stream response and update appropriate chat state

  - message (string)
  - history (array)

- **health_ai_hospital_aid_stream_response_with_state\_**
  Stream response and update appropriate chat state

  - message (string)
  - history (array)

- **health_ai_hospital_aid_handle_helpline_with_state**
  Handle helpline with state management

  - Takes no input parameters

- **health_ai_hospital_aid_handle_tool_selection**
  Handle tool selection from dropdown with separate chat flows

  - tool_name (string, default: "Main Chat")
  - current_chat (array)

- **health_ai_hospital_aid_patients_next_page**
  Go to next page for patients

  - Takes no input parameters

- **health_ai_hospital_aid_patients_prev_page**
  Go to previous page for patients

  - Takes no input parameters

- **health_ai_hospital_aid_refresh_patients**
  Refresh patients table with latest data for given page

  - Takes no input parameters

- **health_ai_hospital_aid_staff_next_page**
  Go to next page for staff

  - Takes no input parameters

- **health_ai_hospital_aid_staff_prev_page**
  Go to previous page for staff

  - Takes no input parameters

- **health_ai_hospital_aid_refresh_staff**
  Refresh staff table with latest data for given page

  - Takes no input parameters

- **health_ai_hospital_aid_rooms_next_page**
  Go to next page for rooms

  - Takes no input parameters

- **health_ai_hospital_aid_rooms_prev_page**
  Go to previous page for rooms

  - Takes no input parameters

- **health_ai_hospital_aid_refresh_rooms**
  Refresh rooms table with latest data for given page

  - Takes no input parameters

- **health_ai_hospital_aid_equipment_next_page**
  Go to next page for equipment

  - Takes no input parameters

- **health_ai_hospital_aid_equipment_prev_page**
  Go to previous page for equipment

  - Takes no input parameters

- **health_ai_hospital_aid_refresh_equipment**
  Refresh equipment table with latest data for given page

  - Takes no input parameters

- **health_ai_hospital_aid_\<lambda>**
  ⚠︎ No description provided in function docstring
  - Takes no input parameters


> Video demonstration showing the MCP server integration using gradio_client showcasing real-time hospital data queries and AI-powered medical consultations.


## 🤖 AI Agent

The primary AI agent powering the medical assistant is the **`meta-llama/Llama-3.3-70B-Instruct`** model, accessed via the Nebius API.

- **Integration:** Managed through the [`NebiusModel`](src/models/nebius_model.py) class, which is initialized and used in [`src/components/interface.py`](src/components/interface.py).
- **Capabilities:**
  - **Medical Consultation:** Answers health-related questions and provides medical information.
  - **Chat Completion:** Engages in natural conversations, maintaining context.
  - **Data Analysis & Presentation:** When provided with data from the hospital database (via the `stream_response` logic in [`src/components/interface.py`](src/components/interface.py)), the AI analyzes this information in conjunction with the user's query. It then generates a comprehensive response including structured data, medical analysis, LaTeX formatting, and recommendations. This process is outlined in the `enhanced_prompt` logic within `stream_response` and [`handle_ai_response`](src/components/interface.py).
  - **Streaming Responses:** Supports streaming of responses for an interactive user experience.
- **Configuration:** Model parameters like temperature and max tokens are handled within the AI interaction functions in [`src/components/interface.py`](src/components/interface.py).

**🏷️ Track 3: Agentic Demo**

H.A.H.A represents a complete agentic application that showcases the power of AI agents in healthcare environments. The system demonstrates:

- **Intelligent Medical Consultation Agent**: Provides contextual medical advice and information
- **Database Query Agent**: Translates natural language queries into structured database operations
- **Data Analysis Agent**: Processes hospital data to provide insights and recommendations
- **Statistics and Prediction**: A modern, responsive dashboard built with Gradio, designed to showcase key hospital statistics and predictive analytics. Users can inquire about the dashboard content by tagging @analysis when asking questions.
- **Multi-modal Interaction**: Seamlessly integrates chat, dashboard visualization, and real-time data


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
    - Copy `.env.template` to `.env`.
    - Fill in your `NEBIUS_API_KEY` and Neon database credentials (e.g., `NEON_HOST`, `NEON_DATABASE`, `NEON_USER`, `NEON_PASSWORD`) in the `.env` file.

## ▶️ Running the Application

- **Development Server (with auto-reload):**
  ```bash
  python dev_server.py
  ```
- **Main Application:**
  ```bash
  python app.py
  ```
  Access the application by navigating to `http://localhost:7860` (or the port configured in [`.env`](.env)).

## 🗄️ Database

The application integrates with a Neon PostgreSQL database containing hospital data across tables like `users`, `patient_records`, `rooms`, `occupancy`, etc. This enables the AI to provide responses based on real-time information. Secure database configuration is handled via [`.env`](.env).



## ⚙️ Future Enhancements

As we continue to evolve H.A.H.A, here are some of the key areas identified for improvement and expansion:

1. **Chat History Access:** Currently, there is no way to retrieve or access previous chat conversations. Adding persistent chat history for each session will enhance continuity and usability.
2. **CRUD Operations on Data Tables:** While users can view hospital data, the application does not yet support Create, Update, or Delete operations. Future updates will allow authorized users to directly modify hospital data.
3. **Improved Prediction Accuracy:** The prediction models used in the current version were optimized for performance due to time constraints. In future releases, we plan to enhance the models for better accuracy and robustness.
4. **Speech-to-Text Integration:** To improve accessibility and ease of use, especially for medical professionals in fast-paced environments, we plan to add voice command and speech-to-text capabilities.



## 📚 References & Tools Used

The development of Hospital AI Helper Aid (H.A.H.A) was made possible through the integration of several powerful tools, libraries, and services:

* **Gradio SDK v5.33.0**: For building the interactive front-end and dashboard components.
* **Python**: Core backend logic, AI orchestration, and server-side functionality.
* **Nebius API**: Used to access the `meta-llama/Llama-3.3-70B-Instruct` model for natural language processing and data analysis.
* **PostgreSQL (Neon)**: Cloud-based relational database system used to store and retrieve real-time hospital data.
* **Model Context Protocol (MCP)**: Enables intelligent integration of AI with structured data through contextual workflows.
* **.env Configuration**: Environment-based secure credential handling.
* **LaTeX Rendering**: For displaying medical metrics like BMI and dosages clearly.
* **Git & GitHub**: Version control and project collaboration.
* **Speech-to-Text Tools (Planned)**: Future plans include integrating solutions like Mozilla DeepSpeech, Whisper, or Web Speech API.

---

🙏 Thank You

We sincerely thank the organizers, mentors, and fellow participants of the hackathon for creating this platform of innovation and collaboration. It has been a rewarding experience to ideate, develop, and present our project — Hospital AI Helper Aid (H.A.H.A) — as part of this event.

We look forward to your feedback and hope this solution contributes meaningfully to the healthcare technology landscape.

**Happy Hacking! 🚀**