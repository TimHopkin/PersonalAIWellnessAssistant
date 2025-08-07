#!/usr/bin/env python3
"""
Data utilities for Personal AI Wellness Assistant
Handles persistent data storage paths for both development and packaged apps.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Union

def get_data_directory() -> Path:
    """
    Get the appropriate data directory for storing user data.
    
    Returns:
        Path: Persistent data directory path
    """
    if getattr(sys, 'frozen', False):
        # Running as packaged app - use Documents folder
        data_dir = Path.home() / "Documents" / "Personal AI Wellness Assistant"
    else:
        # Running in development - use current directory
        data_dir = Path.cwd()
    
    # Create directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir

def get_data_file_path(filename: str) -> Path:
    """
    Get the full path for a data file.
    
    Args:
        filename: Name of the data file (e.g., 'profile.json')
        
    Returns:
        Path: Full path to the data file
    """
    return get_data_directory() / filename

def migrate_existing_data():
    """
    Migrate any existing data files from the current directory to the persistent data directory.
    This is called on first launch of the packaged app.
    """
    if not getattr(sys, 'frozen', False):
        # Skip migration in development mode
        return
    
    data_dir = get_data_directory()
    current_dir = Path.cwd()
    
    # List of data files to migrate
    data_files = [
        'profile.json',
        'wellness_plan.json', 
        'progress_data.json',
        'scheduling_results.json',
        'credentials.json',
        'token.pickle',
        '.env'  # Include .env file for API keys
    ]
    
    migrated_files = []
    
    for filename in data_files:
        source_file = current_dir / filename
        target_file = data_dir / filename
        
        # Only migrate if source exists and target doesn't exist
        if source_file.exists() and not target_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                migrated_files.append(filename)
                print(f"📄 Migrated {filename} to persistent storage")
            except Exception as e:
                print(f"⚠️  Failed to migrate {filename}: {e}")
    
    if migrated_files:
        print(f"✅ Migrated {len(migrated_files)} data files to: {data_dir}")
    else:
        print(f"📁 Using data directory: {data_dir}")

def load_environment_variables():
    """
    Load environment variables from the appropriate .env file location.
    For packaged apps, loads from persistent data directory.
    For development, loads from current directory.
    """
    from dotenv import load_dotenv
    
    if getattr(sys, 'frozen', False):
        # Running as packaged app - load from persistent directory
        env_file = get_data_file_path('.env')
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded environment variables from: {env_file}")
            return True
        else:
            print(f"⚠️  No .env file found at: {env_file}")
            return False
    else:
        # Running in development - load from current directory
        load_dotenv()
        return True

def ensure_data_directory_exists():
    """
    Ensure the data directory exists and is writable.
    
    Returns:
        bool: True if directory is ready, False if there are issues
    """
    try:
        data_dir = get_data_directory()
        
        # Test write access
        test_file = data_dir / ".test_write"
        test_file.write_text("test")
        test_file.unlink()  # Delete test file
        
        return True
        
    except Exception as e:
        print(f"❌ Data directory issue: {e}")
        return False

def get_app_info():
    """
    Get information about the app's data storage setup.
    
    Returns:
        dict: Information about data storage
    """
    data_dir = get_data_directory()
    
    return {
        "data_directory": str(data_dir),
        "is_packaged": getattr(sys, 'frozen', False),
        "is_writable": data_dir.exists() and os.access(data_dir, os.W_OK),
        "existing_files": [f.name for f in data_dir.glob("*.json")] if data_dir.exists() else []
    }

if __name__ == "__main__":
    # Test the data utilities
    print("🔍 Data Utils Test")
    print("=" * 40)
    
    info = get_app_info()
    print(f"Data Directory: {info['data_directory']}")
    print(f"Packaged App: {info['is_packaged']}")
    print(f"Directory Writable: {info['is_writable']}")
    print(f"Existing Files: {info['existing_files']}")
    
    # Test file path generation
    test_files = ['profile.json', 'wellness_plan.json', 'progress_data.json']
    print(f"\nFile Paths:")
    for filename in test_files:
        path = get_data_file_path(filename)
        exists = "✅" if path.exists() else "❌"
        print(f"  {exists} {filename}: {path}")
    
    print(f"\nData directory setup: {'✅ Ready' if ensure_data_directory_exists() else '❌ Issues'}")