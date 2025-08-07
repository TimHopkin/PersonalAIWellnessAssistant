#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Web Application Launcher
Simple launcher for the web interface.
"""

import subprocess
import sys
import time
import webbrowser
from threading import Timer

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    try:
        import flask
    except ImportError:
        missing_deps.append("flask")
    
    try:
        import flask_cors
    except ImportError:
        missing_deps.append("flask-cors")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print("\n📦 Installing missing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_deps)
        print("✅ Dependencies installed!")
    
    return True

def open_browser():
    """Open browser after a delay."""
    time.sleep(2)  # Wait 2 seconds for server to start
    webbrowser.open('http://localhost:8080')

def main():
    """Launch the web application."""
    print("🌟 Personal AI Wellness Assistant - Web Interface")
    print("=" * 55)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("🚀 Starting web application...")
    print("📱 Will automatically open in your browser")
    print("🚪 Press Ctrl+C to stop the server")
    print()
    
    # Start browser opener in background
    Timer(2.0, open_browser).start()
    
    try:
        # Import and run the Flask app
        import app
        print("✅ Flask application loaded successfully")
        print("📍 Server starting at: http://localhost:8080")
        print("-" * 40)
        
        # Run the Flask app
        app.app.run(debug=False, host='0.0.0.0', port=8080, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n👋 Web application stopped!")
        print("Thanks for using Personal AI Wellness Assistant! 💪")
    except Exception as e:
        print(f"\n❌ Error starting web application: {e}")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure port 8080 is available")
        print("  2. Check that all files are in the correct directory")
        print("  3. Try running: python3 app.py")

if __name__ == "__main__":
    main()