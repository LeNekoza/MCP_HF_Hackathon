---
title: Hospital AI Helper Aid
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.32.1
app_file: app.py
pinned: false
license: mit
---

# MCP HF Hackathon - Hospital AI Helper Aid

## 🚀 Model Context Protocol Integration with Hugging Face

This project is part of the MCP (Model Context Protocol) Hugging Face Hackathon, showcasing innovative AI model interactions through a modern Gradio-based web interface.

## 🎯 Project Overview

Our application leverages the Model Context Protocol to create seamless interactions between different AI models from Hugging Face, providing users with an intuitive interface for model experimentation and comparison.

## ✨ Features

- **Multi-Model Support**: Integration with various Hugging Face models
- **Interactive Web Interface**: Built with Gradio for ease of use
- **Model Context Protocol**: Advanced context management capabilities
- **Real-time Processing**: Streaming responses and live updates
- **Configurable Settings**: Customizable model parameters
- **Comprehensive Logging**: Detailed application monitoring

## 🛠️ Tech Stack

- **Frontend**: Gradio (Python-based web interface)
- **Backend**: Python with MCP integration
- **AI Models**: Hugging Face Transformers
- **Configuration**: JSON-based configuration management
- **Testing**: Pytest framework
- **Logging**: Python logging with file and console output

## 📦 Installation

1. **Clone the repository**:

   ```powershell
   git clone <repository-url>
   cd MCP_HF_Hackathon
   ```

2. **Create virtual environment**:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up configuration**:
   - Review and modify `config/app_config.json` as needed
   - Set environment variables if required (see Configuration section)

## 🚀 Quick Start

1. **Run the application**:

   ```powershell
   python app.py
   ```

2. **Open your browser** and navigate to:

   ```
   http://localhost:7860
   ```

3. **Start interacting** with the AI models through the web interface!

## ⚙️ Configuration

The application can be configured through:

### Configuration File

Edit `config/app_config.json` to customize:

- Server settings (host, port)
- Default model selection
- Model parameters (temperature, max tokens)
- MCP protocol settings

### Environment Variables

- `PORT`: Override server port
- `DEBUG`: Enable/disable debug mode
- `SHARE`: Enable/disable Gradio sharing

## 🏗️ Project Structure

```
MCP_HF_Hackathon/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config/               # Configuration files
│   └── app_config.json   # Main app configuration
├── src/                  # Source code
│   ├── components/       # UI components
│   │   └── interface.py  # Main Gradio interface
│   ├── models/          # Model handlers
│   │   └── mcp_handler.py # MCP protocol handler
│   ├── utils/           # Utility functions
│   │   ├── config.py    # Configuration utilities
│   │   ├── helpers.py   # Helper functions
│   │   └── logger.py    # Logging setup
│   └── api/             # API endpoints (future)
├── static/              # Static assets
│   ├── css/            # Custom stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Image assets
├── templates/           # HTML templates (if needed)
├── tests/               # Test files
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── data/                # Data storage
├── docs/                # Documentation
└── logs/                # Application logs (created at runtime)
```

## 🧪 Testing

Run the test suite:

```powershell
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 🔧 Development

### Adding New Models

1. Update the model list in `config/app_config.json`
2. Modify the `MCPHandler` class in `src/models/mcp_handler.py`
3. Add model-specific configurations as needed

### Customizing the Interface

1. Edit `src/components/interface.py` to modify the Gradio interface
2. Add custom CSS in the `load_custom_css()` function
3. Update static assets in the `static/` directory

### Adding New Features

1. Create new modules in the appropriate `src/` subdirectories
2. Update the main `app.py` file to integrate new features
3. Add corresponding tests in the `tests/` directory

## 📊 Monitoring and Logs

- Application logs are stored in the `logs/` directory
- Log level can be configured in the application settings
- Real-time status updates are available in the web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Hackathon Information

This project was developed for the MCP Hugging Face Hackathon 2025, demonstrating innovative applications of the Model Context Protocol with Hugging Face's ecosystem.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the logs in the `logs/` directory
2. Review the configuration in `config/app_config.json`
3. Ensure all dependencies are properly installed
4. Create an issue in the repository for persistent problems

## 🔮 Future Enhancements

- [ ] Add more model providers (OpenAI, Anthropic, etc.)
- [ ] Implement conversation history and context management
- [ ] Add model comparison features
- [ ] Enhance the UI with more customization options
- [ ] Add API endpoints for external integrations
- [ ] Implement user authentication and sessions
- [ ] Add model fine-tuning capabilities
- [ ] Integrate with more MCP features

---

**Happy Hacking! 🚀**