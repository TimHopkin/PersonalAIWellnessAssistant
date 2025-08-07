#!/usr/bin/env python3
"""
Test Google Calendar Authentication
Run this script to test if OAuth flow works properly.
"""

import os
import sys
from calendar_integration import CalendarIntegration
from data_utils import get_data_file_path

def test_calendar_auth():
    print("=== Testing Google Calendar Authentication ===")
    
    # Check if credentials file exists
    creds_file = get_data_file_path('credentials.json')
    print(f"Credentials file: {creds_file}")
    print(f"Exists: {creds_file.exists()}")
    
    if creds_file.exists():
        print("✅ Credentials file found")
    else:
        print("❌ Credentials file not found!")
        return False
    
    # Test calendar integration
    calendar = CalendarIntegration()
    print(f"Calendar credentials path: {calendar.credentials_file}")
    print(f"Calendar token path: {calendar.token_file}")
    
    # Try authentication
    print("\n--- Attempting Authentication ---")
    success = calendar.authenticate()
    
    if success and calendar.service:
        print("✅ Authentication successful! Calendar service available.")
        
        # Test a simple calendar API call
        try:
            calendar_list = calendar.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            print(f"📅 Found {len(calendars)} calendars:")
            for cal in calendars[:3]:  # Show first 3
                print(f"  - {cal.get('summary', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"❌ Calendar API call failed: {e}")
            return False
            
    else:
        print("⚠️  Authentication completed but running in demo mode")
        return False

if __name__ == "__main__":
    # Load environment variables
    from data_utils import load_environment_variables
    load_environment_variables()
    
    success = test_calendar_auth()
    
    if success:
        print("\n🎉 Calendar integration is working!")
    else:
        print("\n❌ Calendar integration needs fixing")