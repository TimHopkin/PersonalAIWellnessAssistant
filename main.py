#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - MVP
Command-line interface for the wellness assistant.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from profile_manager import ProfileManager
from plan_generator import PlanGenerator
from calendar_integration import CalendarIntegration
from progress_tracker import ProgressTracker


class WellnessAssistant:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.plan_generator = PlanGenerator()
        self.calendar_integration = CalendarIntegration()
        self.progress_tracker = ProgressTracker()
        
    def run(self):
        """Main application loop."""
        print("=" * 60)
        print("🌟 PERSONAL AI WELLNESS ASSISTANT - MVP")
        print("=" * 60)
        print("Your AI-powered companion for holistic wellness!")
        print()
        
        try:
            while True:
                choice = self.show_main_menu()
                
                if choice == '1':
                    self.setup_profile()
                elif choice == '2':
                    self.generate_wellness_plan()
                elif choice == '3':
                    self.schedule_activities()
                elif choice == '4':
                    self.track_progress()
                elif choice == '5':
                    self.view_reports()
                elif choice == '6':
                    self.settings_menu()
                elif choice == '0':
                    print("\n👋 Thank you for using Personal AI Wellness Assistant!")
                    print("Remember: Small steps lead to big changes. Keep going! 💪")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay healthy!")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please check your setup and try again.")
    
    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. 👤 Setup/Update Profile")
        print("2. 🎯 Generate Wellness Plan")
        print("3. 📅 Schedule Activities")
        print("4. 📊 Track Progress")
        print("5. 📈 View Reports")
        print("6. ⚙️  Settings")
        print("0. 🚪 Exit")
        print("-" * 40)
        
        return input("Choose an option (0-6): ").strip()
    
    def setup_profile(self):
        """Handle profile setup and updates."""
        print("\n" + "=" * 40)
        print("PROFILE SETUP")
        print("=" * 40)
        
        try:
            profile = self.profile_manager.update_profile()
            print("\n✅ Profile setup complete!")
            self.profile_manager.display_profile(profile)
            
        except Exception as e:
            print(f"❌ Error setting up profile: {e}")
    
    def generate_wellness_plan(self):
        """Generate a new wellness plan."""
        print("\n" + "=" * 40)
        print("WELLNESS PLAN GENERATION")
        print("=" * 40)
        
        # Check if profile exists
        profile = self.profile_manager.load_profile()
        if not profile:
            print("❌ No profile found. Please set up your profile first.")
            return
        
        # Check for existing plan
        existing_plan = self.plan_generator.load_plan()
        if existing_plan:
            print(f"Existing plan found (generated: {existing_plan.get('generated_at', 'Unknown')[:10]})")
            choice = input("Generate a (n)ew plan or (k)eep existing? (n/k): ").lower().strip()
            if choice != 'n':
                print("Keeping existing plan.")
                return
        
        # Get plan duration
        while True:
            try:
                days = int(input("Plan duration in days (3-14, default 7): ") or "7")
                if 3 <= days <= 14:
                    break
                print("Please enter a number between 3 and 14.")
            except ValueError:
                print("Please enter a valid number.")
        
        try:
            print(f"\n🤖 Generating your {days}-day personalized wellness plan...")
            plan = self.plan_generator.generate_plan(profile, days)
            
            print("✅ Plan generated successfully!")
            self.plan_generator.display_plan_summary(plan)
            
            # Offer to schedule immediately
            schedule_now = input("\nWould you like to schedule these activities on your calendar? (y/n): ").lower().strip()
            if schedule_now == 'y':
                self.schedule_activities(plan)
                
        except Exception as e:
            print(f"❌ Error generating plan: {e}")
            print("This might be due to missing API credentials or network issues.")
    
    def schedule_activities(self, plan: Optional[Dict[str, Any]] = None):
        """Schedule activities on Google Calendar."""
        print("\n" + "=" * 40)
        print("CALENDAR SCHEDULING")
        print("=" * 40)
        
        if not plan:
            plan = self.plan_generator.load_plan()
            if not plan:
                print("❌ No wellness plan found. Please generate a plan first.")
                return
        
        # Check calendar authentication
        print("🔑 Authenticating with Google Calendar...")
        if not self.calendar_integration.authenticate():
            print("❌ Calendar authentication failed.")
            print("Please ensure you have:")
            print("  1. Downloaded credentials.json from Google Cloud Console")
            print("  2. Enabled the Google Calendar API")
            print("  3. Set up OAuth2 credentials")
            return
        
        print("✅ Calendar authenticated successfully!")
        
        # Get scheduling preferences
        print("\nScheduling preferences:")
        start_date_input = input("Start date (YYYY-MM-DD, or Enter for tomorrow): ").strip()
        
        if start_date_input:
            try:
                start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Using tomorrow.")
                start_date = datetime.now() + timedelta(days=1)
        else:
            start_date = datetime.now() + timedelta(days=1)
        
        # Get preferred time slots
        print("\nPreferred time slots (press Enter for defaults):")
        morning = input("Morning slot (e.g., 6-9): ").strip()
        evening = input("Evening slot (e.g., 18-21): ").strip()
        
        preferred_times = []
        if morning:
            try:
                start_h, end_h = map(int, morning.split('-'))
                preferred_times.append((start_h, end_h))
            except ValueError:
                print("Invalid morning time format, using default.")
        
        if evening:
            try:
                start_h, end_h = map(int, evening.split('-'))
                preferred_times.append((start_h, end_h))
            except ValueError:
                print("Invalid evening time format, using default.")
        
        if not preferred_times:
            preferred_times = [(6, 9), (18, 21)]  # Default times
        
        try:
            print(f"\n📅 Scheduling activities starting from {start_date.strftime('%B %d, %Y')}...")
            
            result = self.calendar_integration.schedule_wellness_plan(
                plan, start_date, preferred_times
            )
            
            print("✅ Scheduling complete!")
            self.calendar_integration.display_schedule_summary(result)
            
        except Exception as e:
            print(f"❌ Error scheduling activities: {e}")
    
    def track_progress(self):
        """Track daily progress."""
        print("\n" + "=" * 40)
        print("PROGRESS TRACKING")
        print("=" * 40)
        
        plan = self.plan_generator.load_plan()
        if not plan:
            print("❌ No wellness plan found. Please generate a plan first.")
            return
        
        print("Choose tracking method:")
        print("1. Manual progress entry")
        print("2. Device data sync (Garmin/Renpho)")
        print("3. Both manual and device data")
        
        choice = input("Enter choice (1-3): ").strip()
        
        try:
            progress_data = None
            
            if choice in ['1', '3']:
                print("\n📝 Starting manual progress tracking...")
                progress_data = self.progress_tracker.track_manual_progress(plan)
            
            if choice in ['2', '3']:
                print("\n📱 Syncing device data...")
                
                # Garmin data
                garmin_choice = input("Sync Garmin data? (y/n): ").lower().strip()
                if garmin_choice == 'y':
                    garmin_data = self.progress_tracker.get_garmin_data()
                    print(f"Garmin data: {garmin_data.get('steps', 0)} steps, {garmin_data.get('active_minutes', 0)} active minutes")
                
                # Renpho data
                renpho_choice = input("Sync Renpho data? (y/n): ").lower().strip()
                if renpho_choice == 'y':
                    renpho_data = self.progress_tracker.get_renpho_data()
                    print(f"Renpho data: {renpho_data.get('weight_kg', 0)} kg, {renpho_data.get('body_fat_percent', 0)}% body fat")
            
            if not progress_data:
                progress_data = self.progress_tracker.load_progress()
            
            # Check if plan needs adaptation
            if self.progress_tracker.should_adapt_plan(progress_data):
                adapt_choice = input("\n🔄 Your progress suggests the plan could be adapted. Adapt now? (y/n): ").lower().strip()
                if adapt_choice == 'y':
                    self.adapt_plan(progress_data)
            
        except Exception as e:
            print(f"❌ Error tracking progress: {e}")
    
    def view_reports(self):
        """View progress reports and analytics."""
        print("\n" + "=" * 40)
        print("PROGRESS REPORTS")
        print("=" * 40)
        
        progress_data = self.progress_tracker.load_progress()
        daily_logs = progress_data.get('daily_logs', {})
        
        if not daily_logs:
            print("❌ No progress data found. Start tracking to see reports.")
            return
        
        print("Available reports:")
        print("1. Weekly summary")
        print("2. Daily activity log")
        print("3. Wellness trends")
        print("4. Calendar overview")
        
        choice = input("Choose report (1-4): ").strip()
        
        try:
            if choice == '1':
                self.progress_tracker.display_weekly_report(progress_data)
            
            elif choice == '2':
                self.show_daily_log(daily_logs)
            
            elif choice == '3':
                self.show_wellness_trends(progress_data)
            
            elif choice == '4':
                self.show_calendar_overview()
            
            else:
                print("❌ Invalid choice.")
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def show_daily_log(self, daily_logs: Dict[str, Any]):
        """Show daily activity log."""
        print("\n=== Daily Activity Log ===")
        
        # Show last 7 days
        dates = sorted(daily_logs.keys(), reverse=True)[:7]
        
        for date_str in dates:
            log = daily_logs[date_str]
            completed = len(log.get('completed_activities', []))
            skipped = len(log.get('skipped_activities', []))
            
            print(f"\n{date_str}:")
            print(f"  ✅ Completed: {completed}")
            print(f"  ⏭️  Skipped: {skipped}")
            
            if log.get('energy_level'):
                print(f"  ⚡ Energy: {log['energy_level']}/10")
            if log.get('mood_score'):
                print(f"  😊 Mood: {log['mood_score']}/10")
    
    def show_wellness_trends(self, progress_data: Dict[str, Any]):
        """Show wellness trends over time."""
        print("\n=== Wellness Trends ===")
        
        weekly_stats = self.progress_tracker.calculate_weekly_progress(progress_data)
        stats = weekly_stats.get('stats', {})
        
        print(f"Period: {weekly_stats.get('period', 'Unknown')}")
        print(f"Activity completion trend: {stats.get('activity_completion_rate', 0):.1%}")
        print(f"Average energy level: {stats.get('average_energy_level', 0):.1f}/10")
        print(f"Average mood score: {stats.get('average_mood_score', 0):.1f}/10")
        print(f"Total active time: {stats.get('total_duration_completed_minutes', 0)} minutes")
        
        # Simple trend analysis
        daily_logs = progress_data.get('daily_logs', {})
        recent_energy = []
        recent_mood = []
        
        for date_str in sorted(daily_logs.keys())[-7:]:
            log = daily_logs[date_str]
            if log.get('energy_level'):
                recent_energy.append(log['energy_level'])
            if log.get('mood_score'):
                recent_mood.append(log['mood_score'])
        
        if len(recent_energy) >= 2:
            energy_trend = "📈 Improving" if recent_energy[-1] > recent_energy[0] else "📉 Declining"
            print(f"Energy trend: {energy_trend}")
        
        if len(recent_mood) >= 2:
            mood_trend = "📈 Improving" if recent_mood[-1] > recent_mood[0] else "📉 Declining"
            print(f"Mood trend: {mood_trend}")
    
    def show_calendar_overview(self):
        """Show upcoming calendar activities."""
        print("\n=== Calendar Overview ===")
        
        try:
            if not self.calendar_integration.authenticate():
                print("❌ Cannot connect to calendar.")
                return
            
            activities = self.calendar_integration.get_upcoming_activities(7)
            
            if not activities:
                print("No upcoming wellness activities found.")
                return
            
            print(f"Upcoming wellness activities ({len(activities)} found):")
            for activity in activities[:10]:  # Show first 10
                start_time = activity['start_time']
                print(f"  {start_time.strftime('%a %b %d, %I:%M %p')}: {activity['summary']}")
                
        except Exception as e:
            print(f"❌ Error fetching calendar data: {e}")
    
    def adapt_plan(self, progress_data: Dict[str, Any]):
        """Adapt the current plan based on progress."""
        print("\n🔄 Adapting your wellness plan...")
        
        try:
            current_plan = self.plan_generator.load_plan()
            if not current_plan:
                print("❌ No plan to adapt.")
                return
            
            # Calculate progress metrics for adaptation
            weekly_stats = self.progress_tracker.calculate_weekly_progress(progress_data)
            stats = weekly_stats.get('stats', {})
            
            adaptation_data = {
                'completion_rate': stats.get('activity_completion_rate', 0.8),
                'average_energy': stats.get('average_energy_level', 5),
                'active_days': stats.get('active_days', 3),
                'feedback': 'Generated from progress analysis'
            }
            
            adapted_plan = self.plan_generator.adapt_plan(current_plan, adaptation_data)
            
            print("✅ Plan adapted successfully!")
            
            # Ask if user wants to reschedule
            reschedule = input("Reschedule activities on calendar? (y/n): ").lower().strip()
            if reschedule == 'y':
                self.schedule_activities(adapted_plan)
                
        except Exception as e:
            print(f"❌ Error adapting plan: {e}")
    
    def settings_menu(self):
        """Settings and configuration menu."""
        print("\n" + "=" * 40)
        print("SETTINGS")
        print("=" * 40)
        print("1. 🔑 API Configuration")
        print("2. 📁 Data Management")
        print("3. 🎨 Display Preferences")
        print("4. ℹ️  About")
        print("0. ⬅️  Back to Main Menu")
        
        choice = input("Choose option (0-4): ").strip()
        
        if choice == '1':
            self.api_configuration()
        elif choice == '2':
            self.data_management()
        elif choice == '3':
            self.display_preferences()
        elif choice == '4':
            self.show_about()
        elif choice == '0':
            return
        else:
            print("❌ Invalid choice.")
    
    def api_configuration(self):
        """Configure API settings."""
        print("\n=== API Configuration ===")
        
        # Check current API status
        print("Current API Status:")
        print(f"  Grok API: {'✅ Configured' if os.getenv('GROK_API_KEY') else '❌ Not configured'}")
        print(f"  Google Calendar: {'✅ Configured' if os.path.exists('credentials.json') else '❌ Not configured'}")
        print(f"  Garmin: {'✅ Configured' if os.getenv('GARMIN_CLIENT_ID') else '❌ Not configured'}")
        print(f"  Renpho: {'✅ Configured' if os.getenv('RENPHO_EMAIL') else '❌ Not configured'}")
        
        print("\nTo configure APIs, please set up the following:")
        print("1. Create .env file with your API keys")
        print("2. Download credentials.json for Google Calendar")
        print("3. See README.md for detailed setup instructions")
    
    def data_management(self):
        """Manage data files."""
        print("\n=== Data Management ===")
        
        data_files = ['profile.json', 'wellness_plan.json', 'progress_data.json', 'token.pickle']
        
        print("Current data files:")
        for file in data_files:
            exists = "✅ Exists" if os.path.exists(file) else "❌ Not found"
            size = ""
            if os.path.exists(file):
                size = f" ({os.path.getsize(file)} bytes)"
            print(f"  {file}: {exists}{size}")
        
        print("\nData management options:")
        print("1. Backup data")
        print("2. Clear all data")
        print("3. Export progress report")
        
        choice = input("Choose option (1-3, or Enter to skip): ").strip()
        
        if choice == '2':
            confirm = input("⚠️  This will delete ALL data. Type 'DELETE' to confirm: ")
            if confirm == 'DELETE':
                for file in data_files:
                    try:
                        if os.path.exists(file):
                            os.remove(file)
                        print(f"Deleted {file}")
                    except Exception as e:
                        print(f"Error deleting {file}: {e}")
                print("✅ All data cleared.")
        elif choice == '1':
            print("💡 Tip: Copy these files to a backup location manually")
        elif choice == '3':
            print("💡 Progress export functionality coming in future updates")
    
    def display_preferences(self):
        """Display preferences (placeholder for future features)."""
        print("\n=== Display Preferences ===")
        print("💡 Display customization features coming soon!")
        print("Future options will include:")
        print("  • Color themes")
        print("  • Date/time formats") 
        print("  • Unit preferences (metric/imperial)")
        print("  • Notification settings")
    
    def show_about(self):
        """Show about information."""
        print("\n=== About Personal AI Wellness Assistant ===")
        print("Version: MVP 1.0")
        print("Description: AI-powered personal wellness companion")
        print()
        print("Features:")
        print("  • Personalized wellness plan generation using Grok AI")
        print("  • Google Calendar integration for activity scheduling")
        print("  • Progress tracking with device integration stubs")
        print("  • Adaptive planning based on your progress")
        print()
        print("Created as an MVP for personal wellness management.")
        print("Future versions will include enhanced device integrations,")
        print("web interface, and advanced analytics.")


def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    try:
        from googleapiclient.discovery import build
    except ImportError:
        missing_deps.append("google-api-python-client")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_deps.append("python-dotenv")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print("\nPlease install missing dependencies:")
        print(f"  pip install {' '.join(missing_deps)}")
        return False
    
    return True


def main():
    """Main entry point."""
    if not check_dependencies():
        sys.exit(1)
    
    assistant = WellnessAssistant()
    assistant.run()


if __name__ == "__main__":
    main()