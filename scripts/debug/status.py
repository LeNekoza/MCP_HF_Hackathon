#!/usr/bin/env python3
"""
Development Status Dashboard for MCP HF Hackathon
Shows the current status of the development environment
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_command_exists(command):
    """Check if a command exists in the system"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_python_packages():
    """Check if required Python packages are installed"""
    required_packages = ["gradio", "watchdog", "pytest", "black", "flake8", "mypy"]

    installed_packages = {}

    for package in required_packages:
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    f"import {package}; print({package}.__version__)",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            installed_packages[package] = result.stdout.strip()
        except subprocess.CalledProcessError:
            installed_packages[package] = None

    return installed_packages


def check_port_status():
    """Check if the Gradio server is running"""
    try:
        result = subprocess.run(
            ["netstat", "-an"], capture_output=True, text=True, check=True
        )
        return ":7860" in result.stdout
    except subprocess.CalledProcessError:
        return False


def check_files_exist():
    """Check if important files exist"""
    important_files = [
        "app.py",
        "dev_server.py",
        "dev.ps1",
        "src/components/interface.py",
        "requirements.txt",
        ".vscode/settings.json",
        ".vscode/launch.json",
        ".vscode/tasks.json",
    ]

    file_status = {}
    for file_path in important_files:
        file_status[file_path] = os.path.exists(file_path)

    return file_status


def main():
    """Main status checking function"""
    print("=" * 60)
    print("🤖 MCP HF Hackathon - Development Status Dashboard")
    print("=" * 60)

    # Python Environment
    print(f"\n🐍 Python Environment:")
    print(f"   Python Version: {sys.version.split()[0]}")
    print(f"   Python Executable: {sys.executable}")

    # Virtual Environment
    venv_active = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    print(f"   Virtual Environment: {'✅ Active' if venv_active else '❌ Not Active'}")

    # Package Status
    print(f"\n📦 Package Status:")
    packages = check_python_packages()
    for package, version in packages.items():
        status = f"✅ {version}" if version else "❌ Not Installed"
        print(f"   {package}: {status}")

    # Server Status
    print(f"\n🌐 Server Status:")
    server_running = check_port_status()
    print(
        f"   Gradio Server (port 7860): {'✅ Running' if server_running else '❌ Not Running'}"
    )

    # File Status
    print(f"\n📁 File Status:")
    files = check_files_exist()
    for file_path, exists in files.items():
        status = "✅ Exists" if exists else "❌ Missing"
        print(f"   {file_path}: {status}")

    # VS Code Extensions (if in VS Code environment)
    print(f"\n🔧 VS Code Integration:")
    vscode_dir = Path(".vscode")
    if vscode_dir.exists():
        config_files = list(vscode_dir.glob("*.json"))
        print(f"   Configuration Files: ✅ {len(config_files)} files found")

        # Check if workspace file exists
        workspace_files = list(Path(".").glob("*.code-workspace"))
        print(f"   Workspace File: {'✅ Found' if workspace_files else '❌ Not Found'}")
    else:
        print("   VS Code Configuration: ❌ .vscode directory not found")

    # Configuration
    print(f"\n⚙️  Configuration:")
    env_path = ".env"
    if os.path.exists(env_path):
        print(f"   Environment Config: ✅ .env file found")

        # Check for key environment variables
        key_vars = ["SERVER_PORT", "DEFAULT_MODEL", "NEBIUS_API_KEY", "NEON_HOST"]
        for var in key_vars:
            value = os.getenv(var)
            if value:
                # Hide sensitive values
                if "API_KEY" in var or "PASSWORD" in var:
                    display_value = (
                        f"{'*' * 8}...{value[-4:]}" if len(value) > 8 else "***"
                    )
                else:
                    display_value = value
                print(f"   {var}: ✅ {display_value}")
            else:
                print(f"   {var}: ❌ Not set")
    else:
        print(f"   Environment Config: ❌ .env file not found")
        print("   Using default configuration values")

    # Development Tools
    print(f"\n🛠️  Development Tools:")
    tools = ["git", "code"]
    for tool in tools:
        exists = check_command_exists(tool)
        print(f"   {tool}: {'✅ Available' if exists else '❌ Not found'}")

    # Quick Actions
    print(f"\n🚀 Quick Actions:")
    print("   To start development server:")
    print("     Option 1: .\\dev.ps1 -Dev")
    print("     Option 2: .\\venv\\Scripts\\python dev_server.py")
    print("     Option 3: Use VS Code Task 'Run Development Server (Auto-reload)'")
    print()
    print("   To open in VS Code:")
    print("     code MCP_HF_Hackathon.code-workspace")
    print()
    print("   To access the app:")
    print("     http://localhost:7860")

    print("\n" + "=" * 60)
    print("✨ Development environment ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()
