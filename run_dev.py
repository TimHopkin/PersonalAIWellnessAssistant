#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Development Server
Fast development server with hot-reload and debugging capabilities.

Usage:
    python run_dev.py
    
Then open: http://localhost:8080

Features:
- Instant startup (no PyInstaller)
- Hot-reload for templates, static files, and Python code
- Full debug mode with detailed error pages
- Real-time console logging
- No build process required
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def setup_development_environment():
    """Configure the environment for optimal development experience."""
    # Ensure data directory exists
    try:
        from src.data_utils import ensure_data_directory_exists, migrate_existing_data
        ensure_data_directory_exists()
        migrate_existing_data()
        print("✅ Data directory initialized")
    except Exception as e:
        print(f"⚠️ Data directory setup error: {e}")

def main():
    """Start the development server."""
    print("🚀 Starting Personal AI Wellness Assistant - Development Mode")
    print("=" * 60)
    
    # Setup environment
    setup_development_environment()
    
    # Import and configure Flask app
    try:
        from src.app import app
        
        # Enable development features
        app.config.update({
            'ENV': 'development',
            'DEBUG': True,
            'TESTING': False,
            'TEMPLATES_AUTO_RELOAD': True,
            'SEND_FILE_MAX_AGE_DEFAULT': 0,  # Disable static file caching
            'EXPLAIN_TEMPLATE_LOADING': True,  # Show template loading info
        })
        
        print("🔧 Development server configuration:")
        print(f"   • Debug mode: {app.config['DEBUG']}")
        print(f"   • Template auto-reload: {app.config['TEMPLATES_AUTO_RELOAD']}")
        print(f"   • Static file caching: disabled")
        print(f"   • Host: http://127.0.0.1:8080")
        print()
        
        print("💡 Development Tips:")
        print("   • Edit templates, CSS, JS - changes apply immediately")
        print("   • Edit Python files - server auto-restarts")
        print("   • Use browser DevTools for debugging")
        print("   • Check this console for server logs")
        print("   • Press Ctrl+C to stop server")
        print()
        
        print("🌐 Starting server...")
        print("   Main app: http://localhost:8080")
        print("   Chat testing: http://localhost:8080/plan")
        print("   🐛 Debug tools:")
        print("     • Chat test: http://localhost:8080/debug/chat-test")
        print("     • AI status: http://localhost:8080/debug/ai-status")
        print()
        print("📚 Documentation:")
        print("   • Development guide: DEVELOPMENT_GUIDE.md")
        print("   • Debugging playbook: DEBUGGING_PLAYBOOK.md")
        print()
        
        # Start the development server
        app.run(
            host='127.0.0.1',
            port=8080,
            debug=True,
            use_reloader=True,
            use_debugger=True,
            threaded=True,
            extra_files=[
                # Watch additional files for auto-reload
                'static/css/main.css',
                'static/js/main.js',
            ]
        )
        
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("Make sure you're in the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start development server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()