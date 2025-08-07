#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Easy Launcher
Choose how you want to run the application.
"""

import os
import sys

def show_menu():
    """Show launcher menu."""
    print("=" * 60)
    print("🌟 PERSONAL AI WELLNESS ASSISTANT LAUNCHER")
    print("=" * 60)
    print("Choose how you want to run the application:\n")
    print("1. 🧪 Automated Test (shows all features working)")
    print("2. 🎮 Interactive Demo (guided walkthrough)")
    print("3. 🚀 Full Application (requires API setup)")
    print("4. ⚙️  Check Setup Status")
    print("0. 🚪 Exit")
    print("-" * 60)

def check_setup():
    """Check current setup status."""
    print("\n📋 Setup Status Check:")
    print("-" * 40)
    
    # Check Python dependencies
    try:
        import openai
        print("✅ OpenAI library installed")
    except ImportError:
        print("❌ OpenAI library missing - run: pip3 install -r requirements.txt")
    
    try:
        from googleapiclient.discovery import build
        print("✅ Google API libraries installed")
    except ImportError:
        print("❌ Google API libraries missing - run: pip3 install -r requirements.txt")
    
    # Check API credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    grok_key = os.getenv('GROK_API_KEY')
    if grok_key and grok_key != 'demo_key':
        print("✅ Grok API key configured")
    else:
        print("⚠️  Grok API key not found - create .env file with GROK_API_KEY")
    
    if os.path.exists('credentials.json'):
        print("✅ Google Calendar credentials found")
    else:
        print("⚠️  Google Calendar credentials.json not found")
    
    # Check data files
    data_files = ['profile.json', 'wellness_plan.json', 'progress_data.json']
    existing_files = [f for f in data_files if os.path.exists(f)]
    
    if existing_files:
        print(f"📁 Data files: {len(existing_files)}/{len(data_files)} exist")
        for file in existing_files:
            print(f"   ✅ {file}")
    else:
        print("📁 No data files found (will be created on first use)")
    
    print("\n💡 Recommendations:")
    if not grok_key or grok_key == 'demo_key':
        print("   • Get Grok API key from https://x.ai/api ($8/month)")
        print("   • Create .env file: GROK_API_KEY=your_key_here")
    
    if not os.path.exists('credentials.json'):
        print("   • Download Google Calendar credentials from Google Cloud Console")
        print("   • Save as 'credentials.json' in this directory")
    
    print("   • See README.md for detailed setup instructions")

def main():
    """Main launcher."""
    while True:
        show_menu()
        choice = input("Choose option (0-4): ").strip()
        
        if choice == '1':
            print("\n🧪 Running Automated Test...")
            print("This will test all features with sample data.\n")
            os.system('python3 test_app.py')
            
        elif choice == '2':
            print("\n🎮 Starting Interactive Demo...")
            print("Note: Demo may pause waiting for input that won't come in CLI.")
            print("Press Ctrl+C to stop if it hangs.\n")
            try:
                os.system('python3 demo.py')
            except KeyboardInterrupt:
                print("\nDemo stopped.")
                
        elif choice == '3':
            print("\n🚀 Starting Full Application...")
            print("This requires API keys to work fully.\n")
            os.system('python3 main.py')
            
        elif choice == '4':
            check_setup()
            
        elif choice == '0':
            print("\n👋 Thanks for trying Personal AI Wellness Assistant!")
            print("Remember: Small consistent steps lead to big changes! 💪")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
        
        if choice in ['1', '2', '3', '4']:
            input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()