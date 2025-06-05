# VS Code Development Guide for MCP HF Hackathon

This guide will help you set up and use VS Code effectively for developing the MCP HF Hackathon project with live reloading capabilities.

## 🚀 Quick Start

### 1. Open the Project

```bash
# Open VS Code with the workspace file
code MCP_HF_Hackathon.code-workspace
```

### 2. Install Recommended Extensions

When you open the project, VS Code will prompt you to install recommended extensions. Click **"Install All"** or install them manually:

- **Python** (ms-python.python) - Core Python support
- **Pylance** (ms-python.vscode-pylance) - Advanced Python language server
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **Flake8** (ms-python.flake8) - Linting
- **MyPy Type Checker** (ms-python.mypy-type-checker) - Type checking
- **GitLens** (eamodio.gitlens) - Enhanced Git capabilities
- **PowerShell** (ms-vscode.powershell) - PowerShell support

### 3. Setup Environment

```powershell
# Run the setup script
.\dev.ps1 -Install
```

## 🔄 Live Development with Auto-Reload

### Option 1: Using VS Code Tasks (Recommended)

1. **Press `Ctrl+Shift+P`** and type "Tasks: Run Task"
2. Select **"Run Development Server (Auto-reload)"**
3. Your app will start at `http://localhost:7860` with live reload

### Option 2: Using Command Palette

1. **Press `F1`**
2. Search for **"Run Development Server"**
3. The server will start with auto-reload enabled

### Option 3: Using Terminal

```powershell
# Activate virtual environment and start dev server
.\venv\Scripts\Activate.ps1
python dev_server.py
```

### Option 4: Using PowerShell Script

```powershell
.\dev.ps1 -Dev
```

## 🛠️ Available VS Code Tasks

Access these via `Ctrl+Shift+P` → "Tasks: Run Task":

### Build Tasks

- **Setup Project** - Initial project setup
- **Install Dependencies** - Install Python packages
- **Run Gradio App** - Start app normally (no auto-reload)
- **Run Development Server (Auto-reload)** - Start with live reload ⭐
- **Format Code (Black)** - Format all Python files
- **Lint Code (Flake8)** - Check code style
- **Type Check (MyPy)** - Check type annotations
- **Clean Cache** - Remove `__pycache__` files

### Test Tasks

- **Run Tests** - Execute pytest
- **Run Tests with Coverage** - Run tests with coverage report

### Utility Tasks

- **Generate Requirements** - Create requirements_generated.txt
- **Open Logs Directory** - Open logs folder

## 🐛 Debugging

### Debug Configurations Available

Press `F5` or go to Run and Debug panel:

1. **Launch Gradio App** - Debug the main application
2. **Debug Gradio App (Detailed)** - Debug with detailed logging
3. **Run Development Server** - Debug the auto-reload server
4. **Debug Tests** - Debug pytest tests
5. **Debug Specific Test** - Debug currently open test file
6. **Python: Current File** - Debug any Python file

### Setting Breakpoints

- Click in the gutter next to line numbers to set breakpoints
- Use `F9` to toggle breakpoints
- Use `F5` to start debugging, `F10` to step over, `F11` to step into

## 📝 Code Snippets

Type these prefixes and press `Tab` to expand:

- `gr-interface` - Basic Gradio interface
- `gr-blocks` - Gradio Blocks interface
- `gr-event` - Gradio event handler
- `mcp-handler` - MCP handler class
- `py-logger` - Python logger setup
- `py-config` - Configuration loader

## 🔧 Development Workflow

### 1. Starting Development

```powershell
# Option A: Use PowerShell script
.\dev.ps1 -Dev

# Option B: Use VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "Run Development Server (Auto-reload)"
```

### 2. Making Changes

- Edit Python files in `src/`
- Save the file (`Ctrl+S`)
- The development server will automatically detect changes
- Refresh your browser to see updates

### 3. Debugging Issues

- Set breakpoints in VS Code
- Press `F5` to start debugging
- Use the integrated terminal for additional commands

### 4. Running Tests

```powershell
# Run all tests
.\dev.ps1 -Test

# Or use VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "Run Tests"
```

### 5. Code Quality

```powershell
# Format, lint, and type-check code
.\dev.ps1 -Test
```

## 🌐 Browser Integration

### Auto-Open Browser

The development server will automatically open your default browser to `http://localhost:7860`.

### VS Code Simple Browser

You can also use VS Code's built-in browser:

1. `Ctrl+Shift+P`
2. Type "Simple Browser: Show"
3. Enter `http://localhost:7860`

## 📁 Project Structure

```
MCP_HF_Hackathon/
├── .vscode/                 # VS Code configuration
│   ├── settings.json        # Workspace settings
│   ├── launch.json          # Debug configurations
│   ├── tasks.json           # Task definitions
│   ├── extensions.json      # Recommended extensions
│   └── python.code-snippets # Code snippets
├── src/                     # Source code
│   ├── components/          # UI components
│   ├── models/             # MCP handlers
│   └── utils/              # Utilities
├── dev_server.py           # Development server with auto-reload
├── dev.ps1                 # PowerShell development script
├── app.py                  # Main application
└── requirements.txt        # Python dependencies
```

## 🚨 Troubleshooting

### Port Already in Use

```powershell
# Kill existing Python processes
taskkill /F /IM python.exe

# Or use a different port in config/app_config.json
```

### Virtual Environment Issues

```powershell
# Recreate virtual environment
Remove-Item venv -Recurse -Force
python -m venv venv
.\dev.ps1 -Install
```

### Import Errors

```powershell
# Ensure PYTHONPATH is set correctly
$env:PYTHONPATH = "$(Get-Location)\src"
```

### Module Not Found

```powershell
# Install missing dependencies
.\venv\Scripts\pip install -r requirements.txt
```

## 💡 Tips and Tricks

### 1. Quick Actions

- `Ctrl+Shift+P` - Command palette
- ` Ctrl+``  ` - Toggle terminal
- `F5` - Start debugging
- `Ctrl+F5` - Run without debugging
- `F9` - Toggle breakpoint

### 2. File Navigation

- `Ctrl+P` - Quick file open
- `Ctrl+Shift+E` - Explorer panel
- `Ctrl+Shift+F` - Search across files

### 3. Code Quality

- Enable "Format on Save" in settings
- Use `Shift+Alt+F` to format current file
- Use Problems panel (`Ctrl+Shift+M`) to see linting issues

### 4. Git Integration

- Use built-in Git panel (`Ctrl+Shift+G`)
- GitLens provides enhanced Git features
- Use `Ctrl+Enter` in commit message to commit

### 5. Live Reload Best Practices

- Save frequently (`Ctrl+S`) to trigger reloads
- Keep browser dev tools open to see errors
- Use the VS Code integrated terminal for better error visibility

## 🔗 Useful Commands

```powershell
# Development workflow
.\dev.ps1 -Install          # Setup project
.\dev.ps1 -Dev              # Start development
.\dev.ps1 -Test             # Run tests
.\dev.ps1 -Clean            # Clean cache

# Manual commands
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python app.py               # Run app normally
python dev_server.py        # Run with auto-reload
pytest tests/              # Run tests
black src/ tests/ app.py    # Format code
flake8 src/ tests/ app.py   # Lint code
```

## 📚 Additional Resources

- [Gradio Documentation](https://gradio.app/docs/)
- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Project README](README.md)

---

**Happy Coding! 🎉**

The VS Code integration provides you with a powerful development environment with live reloading, debugging, testing, and code quality tools all integrated into your workflow.
