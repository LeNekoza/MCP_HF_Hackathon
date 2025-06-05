# MCP HF Hackathon - Development Setup Script
# PowerShell script for Windows development environment

param(
    [switch]$Install,
    [switch]$Dev,
    [switch]$Test,
    [switch]$Clean,
    [switch]$Help
)

$PROJECT_NAME = "MCP HF Hackathon"
$VENV_PATH = ".\venv"
$PYTHON_CMD = "$VENV_PATH\Scripts\python.exe"
$PIP_CMD = "$VENV_PATH\Scripts\pip.exe"

function Write-Header {
    param($Title)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Write-Step {
    param($Message)
    Write-Host "🔧 $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Test-VirtualEnv {
    return Test-Path $VENV_PATH
}

function Install-Dependencies {
    Write-Header "Installing Dependencies"
    
    if (-not (Test-VirtualEnv)) {
        Write-Step "Creating virtual environment..."
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
    }
    
    Write-Step "Activating virtual environment..."
    & "$VENV_PATH\Scripts\Activate.ps1"
    
    Write-Step "Upgrading pip..."
    & $PIP_CMD install --upgrade pip
    
    Write-Step "Installing requirements..."
    & $PIP_CMD install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed successfully!"
    } else {
        Write-Error "Failed to install dependencies"
        exit 1
    }
}

function Start-DevServer {
    Write-Header "Starting Development Server"
    
    if (-not (Test-VirtualEnv)) {
        Write-Error "Virtual environment not found. Run with -Install first."
        exit 1
    }
    
    Write-Step "Activating virtual environment..."
    & "$VENV_PATH\Scripts\Activate.ps1"
    
    Write-Step "Starting development server with auto-reload..."
    Write-Host "🌐 Your app will be available at: http://localhost:7860" -ForegroundColor Yellow
    Write-Host "🔄 Auto-reload enabled - edit files to see changes" -ForegroundColor Yellow
    Write-Host "📝 Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    & $PYTHON_CMD dev_server.py
}

function Run-Tests {
    Write-Header "Running Tests"
    
    if (-not (Test-VirtualEnv)) {
        Write-Error "Virtual environment not found. Run with -Install first."
        exit 1
    }
    
    Write-Step "Activating virtual environment..."
    & "$VENV_PATH\Scripts\Activate.ps1"
    
    Write-Step "Running pytest..."
    & $PYTHON_CMD -m pytest tests/ -v
    
    Write-Step "Running code formatting check..."
    & $PYTHON_CMD -m black src/ tests/ app.py --check
    
    Write-Step "Running linting..."
    & $PYTHON_CMD -m flake8 src/ tests/ app.py
    
    Write-Step "Running type checking..."
    & $PYTHON_CMD -m mypy src/
}

function Clean-Project {
    Write-Header "Cleaning Project"
    
    Write-Step "Removing Python cache files..."
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    
    Write-Step "Removing test cache..."
    Remove-Item ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item ".mypy_cache" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Step "Removing logs..."
    Get-ChildItem -Path "logs" -Name "*.log" | Remove-Item -Force -ErrorAction SilentlyContinue
    
    Write-Success "Project cleaned!"
}

function Show-Help {
    Write-Header "$PROJECT_NAME - Development Helper"
    
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 -Install    Install dependencies and setup environment" -ForegroundColor White
    Write-Host "  .\dev.ps1 -Dev        Start development server with auto-reload" -ForegroundColor White
    Write-Host "  .\dev.ps1 -Test       Run tests, linting, and type checking" -ForegroundColor White
    Write-Host "  .\dev.ps1 -Clean      Clean cache files and logs" -ForegroundColor White
    Write-Host "  .\dev.ps1 -Help       Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 -Install           # First time setup" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 -Dev               # Start developing" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 -Test              # Run all tests" -ForegroundColor Gray
    Write-Host ""
    Write-Host "VS Code Integration:" -ForegroundColor Yellow
    Write-Host "  - Use Ctrl+Shift+P and search 'Tasks: Run Task'" -ForegroundColor Gray
    Write-Host "  - Or press F1 and select 'Run Development Server'" -ForegroundColor Gray
    Write-Host "  - Use F5 to start debugging" -ForegroundColor Gray
    Write-Host ""
}

# Main script logic
if ($Help -or (-not $Install -and -not $Dev -and -not $Test -and -not $Clean)) {
    Show-Help
    exit 0
}

if ($Install) {
    Install-Dependencies
}

if ($Dev) {
    Start-DevServer
}

if ($Test) {
    Run-Tests
}

if ($Clean) {
    Clean-Project
}

Write-Host ""
