#!/usr/bin/env python3
"""
Development Server with Auto-reload for MCP HF Hackathon
Provides live reloading similar to nodemon for Node.js
"""

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class GradioReloader(FileSystemEventHandler):
    """File system event handler for auto-reloading Gradio application"""

    def __init__(self, script_path: str, watch_paths: list):
        self.script_path = script_path
        self.watch_paths = watch_paths
        self.process: Optional[subprocess.Popen] = None
        self.last_restart = 0
        self.restart_delay = 1  # Minimum seconds between restarts
        self._first_launch = True  # Track if this is the first launch        print("🔧 Development server initialized")
        print(f"📂 Watching: {', '.join(watch_paths)}")
        print(f"🚀 Script: {script_path}")

        self.restart_server()

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return  # Convert path to string safely
        try:
            src_path = str(event.src_path)
        except Exception:
            src_path = repr(event.src_path)

        # Only reload on Python file changes
        if not src_path.endswith(".py"):
            return

        # Ignore cache files and logs
        ignore_patterns = ["__pycache__", ".pyc", "logs/", "venv/"]
        if any(ignore in src_path for ignore in ignore_patterns):
            return

        # Prevent rapid successive restarts
        current_time = time.time()
        if current_time - self.last_restart < self.restart_delay:
            return

        print(f"🔄 File changed: {src_path}")
        self.restart_server()

    def restart_server(self):
        """Restart the Gradio server"""
        if self.process:
            print("🛑 Stopping Gradio server...")
            try:
                # Graceful shutdown
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing server...")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")

        print("🚀 Starting Gradio server...")

        # Set up environment
        env = os.environ.copy()
        env["GRADIO_ANALYTICS_ENABLED"] = "False"
        env["PYTHONPATH"] = os.path.join(os.getcwd(), "src")
        env["GRADIO_DEBUG"] = "1"
        env["GRADIO_PREVENT_THREAD_LOCK"] = "True"

        # Prevent opening new browser tabs on restart (only open on first launch)
        if hasattr(self, "_first_launch") and not self._first_launch:
            env["NO_BROWSER"] = "1"
        else:
            self._first_launch = False

        try:
            # Start new process
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            self.last_restart = (
                time.time()
            )  # Start output monitoring in separate thread
            threading.Thread(target=self._monitor_output, daemon=True).start()

            print("✅ Server started successfully")

        except Exception as e:
            print(f"❌ Failed to start server: {e}")

    def _monitor_output(self):
        """Monitor and display server output"""
        if not self.process or not self.process.stdout:
            return

        try:
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    # Filter out excessive Gradio logs
                    if not any(
                        noise in line.lower()
                        for noise in ["running on", "to create a public link"]
                    ):
                        print(f"📱 {line.strip()}")

                        # Check for server ready message
                        if "running on local url" in line.lower():
                            print("🌐 Server is ready!")

        except Exception as e:
            print(f"⚠️  Output monitoring error: {e}")

    def cleanup(self):
        """Clean up resources"""
        if self.process:
            print("🧹 Cleaning up...")
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")


def main():
    """Main development server function"""

    # Configuration
    script_path = "app.py"
    watch_paths = ["src/", "config/", "static/", "scripts/"]

    print("=" * 60)
    print("🤖 MCP HF Hackathon - Development Server")
    print("=" * 60)

    # Validate script exists
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        print("Please ensure app.py exists in the project root")
        return 1

    # Validate watch paths
    existing_paths = [path for path in watch_paths if os.path.exists(path)]
    if not existing_paths:
        print(f"❌ No watch paths found: {watch_paths}")
        return 1  # Check if virtual environment is activated
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Virtual environment not detected. Consider activating venv first.")

    # Install watchdog if not available
    try:
        import watchdog
    except ImportError:
        print("📦 Installing watchdog for file monitoring...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
        import watchdog

    # Set up file watcher
    event_handler = GradioReloader(script_path, existing_paths)
    observer = Observer()

    for path in existing_paths:
        observer.schedule(event_handler, path, recursive=True)
        print(f"👀 Watching: {path}")

    observer.start()

    print("\n" + "=" * 60)
    print("🌐 Your Gradio app will be available at: http://localhost:7860")
    print("🔄 Auto-reload is enabled - edit Python files to see changes")
    print("📝 Press Ctrl+C to stop the development server")
    print("=" * 60 + "\n")

    # Set up signal handlers for clean shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        observer.stop()
        event_handler.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)

            # Check if main process is still running
            if event_handler.process and event_handler.process.poll() is not None:
                print("⚠️  Server process died, restarting...")
                event_handler.restart_server()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down development server...")
    finally:
        observer.stop()
        event_handler.cleanup()
        observer.join()
        print("👋 Development server stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
