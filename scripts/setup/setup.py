#!/usr/bin/env python3
"""
Setup script for MCP HF Hackathon project
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    if os.path.exists("venv"):
        print("✓ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_and_install_requirements():
    """Install requirements in virtual environment"""
    print("Installing requirements...")
    
    # Different activation commands for different platforms
    if os.name == 'nt':  # Windows
        activate_cmd = ".\\venv\\Scripts\\Activate.ps1"
        pip_cmd = ".\\venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "./venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
        return False
    
    print("✓ Requirements installed successfully")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "data/models", "data/cache"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    return True

def validate_config():
    """Validate configuration file"""
    config_path = "config/app_config.json"
    
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ["server_name", "server_port", "default_model"]
        for key in required_keys:
            if key not in config:
                print(f"Error: Missing required configuration key: {key}")
                return False
        
        print("✓ Configuration file validated")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        return False

def run_tests():
    """Run basic tests to verify setup"""
    print("Running basic tests...")
    
    # Different python commands for different platforms
    if os.name == 'nt':  # Windows
        python_cmd = ".\\venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "./venv/bin/python"
    
    # Test imports
    test_command = f'{python_cmd} -c "import gradio; import sys; sys.path.append(\'src\'); from utils.config import load_config; print(\'✓ Basic imports successful\')"'
    
    return run_command(test_command, "Testing basic imports")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\Activate.ps1")
    else:  # Unix/Linux/macOS  
        print("   source venv/bin/activate")
    
    print("\n2. Run the application:")
    print("   python app.py")
    
    print("\n3. Open your browser and navigate to:")
    print("   http://localhost:7860")
    
    print("\n4. (Optional) Run tests:")
    print("   pytest")
    
    print("\nFor more information, see README.md")
    print("="*60)

def main():
    """Main setup function"""
    print("MCP HF Hackathon - Project Setup")
    print("="*40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Checking virtual environment", create_virtual_environment),
        ("Installing dependencies", activate_and_install_requirements),
        ("Creating directories", create_directories),
        ("Validating configuration", validate_config),
        ("Running basic tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            sys.exit(1)
        print(f"✓ Completed: {step_name}")
    
    print_next_steps()

if __name__ == "__main__":
    main()
