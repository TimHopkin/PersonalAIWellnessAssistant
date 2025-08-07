#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Desktop Application
PyWebView wrapper for the Flask web interface.
"""

import webview
import threading
import time
import sys
import os
from flask import Flask
from data_utils import migrate_existing_data, ensure_data_directory_exists, load_environment_variables, get_data_directory

# Import the existing Flask app
from app import app

class DesktopApp:
    def __init__(self):
        self.flask_app = app
        self.flask_thread = None
        self.server_started = False
        
    def start_flask_server(self):
        """Start the Flask server in a separate thread."""
        try:
            # Configure Flask for desktop use with development features
            self.flask_app.config['ENV'] = 'development'
            self.flask_app.config['DEBUG'] = True
            self.flask_app.config['TEMPLATES_AUTO_RELOAD'] = True
            self.flask_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching
            
            # Start Flask server
            self.flask_app.run(
                host='127.0.0.1',
                port=8080,
                debug=False,  # Keep False to avoid reloader conflicts with webview
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            print(f"Error starting Flask server: {e}")
            
    def wait_for_server(self, timeout=10):
        """Wait for Flask server to start."""
        import requests
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://127.0.0.1:8080/', timeout=1)
                if response.status_code == 200:
                    self.server_started = True
                    return True
            except:
                pass
            time.sleep(0.1)
        
        return False
    
    def on_window_closed(self):
        """Handle window closure."""
        print("Shutting down Personal AI Wellness Assistant...")
        # The Flask server will shut down when the main thread exits
        os._exit(0)
    
    def run(self):
        """Run the desktop application."""
        print("=" * 60)
        print("🌟 Personal AI Wellness Assistant - Desktop Application")
        print("=" * 60)
        print("🔧 Development Mode: Template auto-reload enabled")
        print("🗑️  Cache: Cleared on startup")
        print("🐛 Debug: DevTools available (right-click → Inspect)")
        print()
        print("Starting Personal AI Wellness Assistant...")
        
        # Start Flask server in background thread
        self.flask_thread = threading.Thread(
            target=self.start_flask_server,
            daemon=True
        )
        self.flask_thread.start()
        
        # Wait for server to start
        print("Starting web server...")
        if not self.wait_for_server():
            print("Error: Could not start web server")
            return
        
        print("Server started successfully")
        print("Opening application window...")
        
        # Create and start the webview window with cache busting
        import time
        cache_buster = int(time.time())  # Use current timestamp to bust cache
        window = webview.create_window(
            title='Personal AI Wellness Assistant',
            url=f'http://127.0.0.1:8080?v={cache_buster}',
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True,
            shadow=True,
            on_top=False,
            text_select=False
        )
        
        # Configure webview settings with cache clearing
        webview.settings = {
            'ALLOW_DOWNLOADS': True,
            'ALLOW_FILE_URLS': True,
            'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
            'OPEN_DEVTOOLS_IN_DEBUG': True,  # Enable devtools for debugging
            'IGNORE_SSL_ERRORS': False,
            'CLEAR_CACHE_ON_START': True  # Clear cache on start (if supported)
        }
        
        # Start the webview (this will block until window is closed)
        try:
            webview.start(
                debug=False,
                http_server=False,  # We're using our own Flask server
                private_mode=False
            )
        except KeyboardInterrupt:
            pass
        finally:
            self.on_window_closed()

def main():
    """Main entry point for desktop application."""
    print("=" * 60)
    print("🌟 PERSONAL AI WELLNESS ASSISTANT - DESKTOP APP")
    print("=" * 60)
    
    # Check if running as a packaged app or in development
    if getattr(sys, 'frozen', False):
        # Running as packaged app
        print("Running as packaged application")
        print(f"App bundle resources: {sys._MEIPASS}")
        
        # Set the working directory to the app bundle's Resources for resource access
        os.chdir(sys._MEIPASS)
        
        # Migrate any existing data to persistent location
        migrate_existing_data()
        
        # Load environment variables from persistent location
        print("Loading environment variables from persistent storage...")
        load_environment_variables()
        
        # Set working directory to persistent data directory for file operations
        persistent_dir = get_data_directory()
        print(f"Setting data working directory to: {persistent_dir}")
        
    else:
        # Running in development
        print("Running in development mode")
        print(f"Working directory: {os.getcwd()}")
        
        # Load environment variables from current directory
        load_environment_variables()
    
    # Ensure data directory is ready
    if not ensure_data_directory_exists():
        print("❌ Warning: Data directory setup failed. Profile saving may not work.")
        print("Please check file permissions and try again.")
    else:
        print("✅ Data directory ready for use")
    
    try:
        # Create and run the desktop app
        desktop_app = DesktopApp()
        desktop_app.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running desktop application: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Application closed.")

if __name__ == '__main__':
    main()