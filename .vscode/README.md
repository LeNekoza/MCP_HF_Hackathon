# VS Code Integration Guide

This document explains how to use the VS Code integration features for the MCP HF Hackathon project.

## 🚀 Quick Start

### Option 1: Using VS Code Workspace

1. Open the `MCP_HF_Hackathon.code-workspace` file in VS Code
2. Install recommended extensions when prompted
3. Press `Ctrl+Shift+P` and run "Tasks: Run Task" → "Quick Start - Development Server"

### Option 2: Using PowerShell Script

```powershell
# First time setup
.\dev.ps1 -Install

# Start development server
.\dev.ps1 -Dev

# Run tests
.\dev.ps1 -Test
```

### Option 3: Using VS Code Tasks

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select from available tasks:
   - "Run Development Server (Auto-reload)"
   - "Run Gradio App"
   - "Run Tests"
   - "Format Code (Black)"
   - "Lint Code (Flake8)"

## 🔧 Development Features

### Auto-reload Development Server

The development server provides live reloading similar to nodemon:

```powershell
# Start with auto-reload
python dev_server.py

# Or using the task
Ctrl+Shift+P → "Tasks: Run Task" → "Run Development Server (Auto-reload)"
```

**Features:**

- 🔄 Automatically restarts when Python files change
- 🌐 Opens browser automatically
- 📝 Real-time file monitoring
- 🛑 Graceful shutdown handling
- 📱 Server output monitoring

### Debugging

Use F5 or the debug configurations:

1. **Launch Gradio App** - Standard debugging
2. **Debug Gradio App (Detailed)** - With verbose logging
3. **Run Development Server** - Debug the auto-reload server
4. **Debug Tests** - Run pytest with debugging
5. **Python: Current File** - Debug any Python file

### Code Quality Tools

#### Formatting (Black)

- **Auto-format on save**: Enabled by default
- **Manual formatting**: `Ctrl+Shift+P` → "Format Document"
- **Task**: "Format Code (Black)"

#### Linting (Flake8)

- **Real-time linting**: Shows errors in Problems panel
- **Manual linting**: Task "Lint Code (Flake8)"
- **Configuration**: Line length 100, ignores E203,W503

#### Type Checking (MyPy)

- **Real-time checking**: Enabled for `src/` directory
- **Manual checking**: Task "Type Check (MyPy)"

## 📁 Project Structure Integration

```
.vscode/
├── settings.json          # VS Code workspace settings
├── launch.json           # Debug configurations
├── tasks.json            # Build and run tasks
├── extensions.json       # Recommended extensions
└── python.code-snippets  # Code snippets for Gradio/MCP

dev_server.py             # Auto-reload development server
dev.ps1                   # PowerShell development helper
MCP_HF_Hackathon.code-workspace  # VS Code workspace file
```

## 🎯 Code Snippets

Type these prefixes and press Tab:

- `gr-interface` - Basic Gradio interface
- `gr-blocks` - Gradio Blocks interface
- `mcp-handler` - MCP handler class
- `gr-event` - Gradio event handler
- `py-logger` - Python logger setup
- `py-config` - Config loader function

## 🔍 Search and Navigation

### Configured Exclusions

- `__pycache__/` folders
- `*.pyc` files
- `venv/` directory
- `logs/` directory
- `.pytest_cache/`
- `.mypy_cache/`

### IntelliSense Features

- Auto-import completions
- Function parameter completion
- Type hints and documentation
- Auto-search paths for `src/` modules

## 🧪 Testing Integration

### Pytest Integration

- **Discover tests**: Automatic test discovery
- **Run tests**: Use Test Explorer or tasks
- **Debug tests**: Set breakpoints and debug
- **Coverage**: Task "Run Tests with Coverage"

### Test Commands

```powershell
# Run all tests
.\dev.ps1 -Test

# Or use VS Code tasks
Ctrl+Shift+P → "Tasks: Run Task" → "Run Tests"
```

## 🛠 Utility Tasks

### Project Management

- **Setup Project** - Run setup.py
- **Install Dependencies** - Install requirements.txt
- **Clean Cache** - Remove Python cache files
- **Generate Requirements** - Create requirements_generated.txt
- **Open Logs Directory** - Open logs folder

### Environment Management

- **Virtual Environment**: Automatically detected and activated
- **Python Path**: Configured for `src/` module imports
- **Environment Variables**: Support for `.env` files

## 🌐 Browser Integration

### Automatic Browser Opening

- Development server opens browser automatically
- Uses http://localhost:7860 by default
- Can be disabled with `NO_BROWSER=1` environment variable

### Live Reloading Workflow

1. Start development server: `.\dev.ps1 -Dev`
2. Open http://localhost:7860 in browser
3. Edit Python files in VS Code
4. Server automatically restarts
5. Refresh browser to see changes

## ⌨️ Keyboard Shortcuts

### Built-in VS Code Shortcuts

- `F5` - Start debugging
- `Ctrl+F5` - Run without debugging
- `Ctrl+Shift+P` - Command palette
- `Ctrl+Shift+~` - New terminal
- ` Ctrl+``  ` - Toggle terminal

### Custom Tasks

- `Ctrl+Shift+P` → "Tasks: Run Task" → Select task
- `Ctrl+Shift+F5` - Restart debugging session

## 🔧 Configuration Files

### settings.json

- Python interpreter path
- Formatting and linting settings
- File associations
- Terminal configuration

### launch.json

- Debug configurations for different scenarios
- Environment variable setup
- Debugging options

### tasks.json

- Build and run tasks
- Problem matchers for error detection
- Background task configuration

## 📝 Tips and Best Practices

### Development Workflow

1. Use the development server for rapid iteration
2. Set breakpoints for debugging complex logic
3. Use code snippets for common patterns
4. Run tests frequently with the Test Explorer
5. Format code on save (auto-enabled)

### Performance

- Development server monitors only Python files
- Excludes cache directories from search
- Uses efficient file watching with debouncing

### Debugging

- Use "Debug Gradio App (Detailed)" for verbose logging
- Set breakpoints in event handlers
- Use the integrated terminal for manual testing

### Code Quality

- Black formatting on save
- Real-time Flake8 linting
- MyPy type checking
- Automatic import organization

## 🆘 Troubleshooting

### Common Issues

**Virtual Environment Not Found**

```powershell
# Recreate virtual environment
python -m venv venv
.\dev.ps1 -Install
```

**Module Import Errors**

- Check PYTHONPATH in VS Code settings
- Ensure virtual environment is activated
- Verify `src/` is in Python path

**Development Server Issues**

```powershell
# Check if port is in use
netstat -an | findstr :7860

# Kill process using port
taskkill /F /PID <process_id>
```

**Linting Errors**

- Check Flake8 configuration in settings.json
- Update line length settings if needed
- Disable specific rules in setup.cfg

### Getting Help

1. Check the integrated terminal for error messages
2. Use the Problems panel for linting/type errors
3. Check the Output panel for task execution logs
4. Use the Debug Console during debugging sessions

---

For more information, see the main [README.md](../README.md) file.
