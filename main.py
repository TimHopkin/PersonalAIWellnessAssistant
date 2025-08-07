#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Main Entry Point
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

def main():
    """Main entry point for the application"""
    from src.desktop_app import DesktopApp
    
    app = DesktopApp()
    app.run()

if __name__ == '__main__':
    main()