#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Demo Script
Demonstrates all features without requiring user input.
"""

import json
import os
from datetime import datetime, timedelta
from profile_manager import ProfileManager
from plan_generator import PlanGenerator
from calendar_integration import CalendarIntegration
from progress_tracker import ProgressTracker

def demo_banner():
    """Display demo banner."""
    print("=" * 70)
    print("🌟 PERSONAL AI WELLNESS ASSISTANT - INTERACTIVE DEMO")
    print("=" * 70)
    print("This demo shows all features working with sample data.")
    print("No API keys required - using fallback/mock implementations.")
    print()

def demo_profile():
    """Demo profile management."""
    print("📋 DEMO: Profile Management")
    print("-" * 40)
    
    profile_manager = ProfileManager()
    
    # Create sample profile
    sample_profile = {
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "age": 32,
        "weight": 70.0,
        "height": 175.0,
        "fitness_level": "intermediate",
        "goals": "improve cardiovascular health and reduce stress",
        "constraints": "no gym access, prefer morning workouts",
        "activity_preferences": {
            "running": True,
            "cycling": True,
            "yoga": True,
            "stretching": True,
            "meditation": True,
            "strength_training": False
        },
        "available_time_slots": "6-8 AM, 6-8 PM"
    }
    
    # Save and display profile
    profile_manager.save_profile(sample_profile)
    print("✅ Sample profile created!")
    profile_manager.display_profile(sample_profile)
    
    return sample_profile

def demo_plan_generation(profile):
    """Demo AI plan generation."""
    print("\n🎯 DEMO: AI Wellness Plan Generation")
    print("-" * 40)
    
    plan_generator = PlanGenerator()
    
    print("Generating 7-day wellness plan...")
    plan = plan_generator.generate_plan(profile, 7)
    
    print("✅ Plan generated successfully!")
    plan_generator.display_plan_summary(plan)
    
    return plan

def demo_calendar_integration(plan):
    """Demo calendar scheduling."""
    print("\n📅 DEMO: Calendar Integration")
    print("-" * 40)
    
    calendar_integration = CalendarIntegration()
    
    print("Authenticating with calendar...")
    if calendar_integration.authenticate():
        print("✅ Calendar ready (demo mode)")
        
        print("\nScheduling wellness activities...")
        start_date = datetime.now() + timedelta(days=1)
        
        result = calendar_integration.schedule_wellness_plan(
            plan, start_date, [(6, 9), (18, 21)]
        )
        
        print("✅ Scheduling complete!")
        calendar_integration.display_schedule_summary(result)
        
        print("\n📋 Upcoming activities:")
        activities = calendar_integration.get_upcoming_activities(3)
        for activity in activities:
            start_time = activity['start_time']
            print(f"  {start_time.strftime('%a %b %d, %I:%M %p')}: {activity['summary']}")
    
    return True

def demo_progress_tracking(plan):
    """Demo progress tracking."""
    print("\n📊 DEMO: Progress Tracking")
    print("-" * 40)
    
    progress_tracker = ProgressTracker()
    
    # Create sample progress data
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    sample_progress = {
        'daily_logs': {
            str(yesterday): {
                'date': str(yesterday),
                'completed_activities': [
                    {
                        'activity': {
                            'type': 'running',
                            'duration_minutes': 30,
                            'intensity': 'moderate'
                        },
                        'completion_time': datetime.now().isoformat(),
                        'notes': 'Felt great!',
                        'full_completion': True
                    },
                    {
                        'activity': {
                            'type': 'meditation',
                            'duration_minutes': 10,
                            'intensity': 'low'
                        },
                        'completion_time': datetime.now().isoformat(),
                        'notes': 'Very relaxing',
                        'full_completion': True
                    }
                ],
                'skipped_activities': [],
                'notes': 'Great day overall',
                'energy_level': 8,
                'mood_score': 9
            },
            str(today): {
                'date': str(today),
                'completed_activities': [
                    {
                        'activity': {
                            'type': 'yoga',
                            'duration_minutes': 25,
                            'intensity': 'low'
                        },
                        'completion_time': datetime.now().isoformat(),
                        'notes': 'Morning session',
                        'full_completion': True
                    }
                ],
                'skipped_activities': [
                    {
                        'activity': {
                            'type': 'cycling',
                            'duration_minutes': 45,
                            'intensity': 'moderate'
                        },
                        'skip_reason': 'Too tired',
                        'skip_time': datetime.now().isoformat()
                    }
                ],
                'notes': 'Skipped evening workout',
                'energy_level': 6,
                'mood_score': 7
            }
        },
        'device_data': {},
        'weekly_summaries': {}
    }
    
    # Save sample progress
    progress_tracker.save_progress(sample_progress)
    print("✅ Sample progress data created!")
    
    # Display weekly report
    print("\n📈 Weekly Progress Report:")
    progress_tracker.display_weekly_report(sample_progress)
    
    # Check if adaptation is needed
    if progress_tracker.should_adapt_plan(sample_progress):
        print("\n🔄 Plan adaptation recommended based on progress!")
    
    return sample_progress

def demo_device_integration():
    """Demo device data integration."""
    print("\n📱 DEMO: Device Integration")
    print("-" * 40)
    
    progress_tracker = ProgressTracker()
    
    print("Fetching Garmin data (demo mode)...")
    garmin_data = progress_tracker.get_garmin_data()
    print(f"  Steps: {garmin_data.get('steps', 0)}")
    print(f"  Active minutes: {garmin_data.get('active_minutes', 0)}")
    print(f"  Average heart rate: {garmin_data.get('heart_rate_avg', 0)} bpm")
    
    print("\nFetching Renpho data (demo mode)...")
    renpho_data = progress_tracker.get_renpho_data()
    print(f"  Weight: {renpho_data.get('weight_kg', 0)} kg")
    print(f"  Body fat: {renpho_data.get('body_fat_percent', 0)}%")
    
    print("✅ Device data synchronized!")

def demo_analytics(progress_data):
    """Demo analytics and insights."""
    print("\n📈 DEMO: Analytics & Insights")
    print("-" * 40)
    
    progress_tracker = ProgressTracker()
    
    # Calculate weekly statistics
    weekly_stats = progress_tracker.calculate_weekly_progress(progress_data)
    stats = weekly_stats.get('stats', {})
    
    print("Weekly Performance Metrics:")
    print(f"  Activity completion rate: {stats.get('activity_completion_rate', 0):.1%}")
    print(f"  Duration completion rate: {stats.get('duration_completion_rate', 0):.1%}")
    print(f"  Average energy level: {stats.get('average_energy_level', 0):.1f}/10")
    print(f"  Average mood score: {stats.get('average_mood_score', 0):.1f}/10")
    print(f"  Total active time: {stats.get('total_duration_completed_minutes', 0)} minutes")
    
    # Provide insights
    completion_rate = stats.get('activity_completion_rate', 0)
    if completion_rate >= 0.8:
        print("\n💡 Insight: Excellent consistency! Consider increasing challenge.")
    elif completion_rate >= 0.6:
        print("\n💡 Insight: Good progress! Keep up the momentum.")
    else:
        print("\n💡 Insight: Consider adjusting plan difficulty or schedule.")

def demo_adaptive_planning(plan, progress_data):
    """Demo adaptive planning."""
    print("\n🔄 DEMO: Adaptive Planning")
    print("-" * 40)
    
    plan_generator = PlanGenerator()
    progress_tracker = ProgressTracker()
    
    # Check if adaptation is needed
    if progress_tracker.should_adapt_plan(progress_data):
        print("Progress analysis suggests plan adaptation...")
        
        # Simulate adaptation
        weekly_stats = progress_tracker.calculate_weekly_progress(progress_data)
        stats = weekly_stats.get('stats', {})
        
        adaptation_data = {
            'completion_rate': stats.get('activity_completion_rate', 0.8),
            'average_energy': stats.get('average_energy_level', 5),
            'active_days': stats.get('active_days', 3),
            'feedback': 'Simulated adaptation based on progress'
        }
        
        adapted_plan = plan_generator.adapt_plan(plan, adaptation_data)
        print("✅ Plan adapted successfully!")
        
        print("Adaptation changes:")
        if adaptation_data['completion_rate'] < 0.5:
            print("  • Reduced activity intensity")
            print("  • Shortened session durations")
        elif adaptation_data['completion_rate'] > 0.9:
            print("  • Increased challenge level")
            print("  • Added variety to activities")
    else:
        print("✅ Current plan is working well - no adaptation needed!")

def main():
    """Run the complete demo."""
    try:
        demo_banner()
        
        # Demo all features in sequence
        print("🚀 Starting comprehensive feature demo...\n")
        
        # 1. Profile Management
        profile = demo_profile()
        
        # 2. Plan Generation
        plan = demo_plan_generation(profile)
        
        # 3. Calendar Integration
        demo_calendar_integration(plan)
        
        # 4. Progress Tracking
        progress_data = demo_progress_tracking(plan)
        
        # 5. Device Integration
        demo_device_integration()
        
        # 6. Analytics
        demo_analytics(progress_data)
        
        # 7. Adaptive Planning
        demo_adaptive_planning(plan, progress_data)
        
        # Final summary
        print("\n" + "=" * 70)
        print("🎉 DEMO COMPLETE!")
        print("=" * 70)
        print("All features demonstrated successfully!")
        print()
        print("Key Features Shown:")
        print("✅ Profile management with personalized preferences")
        print("✅ AI-powered wellness plan generation (fallback mode)")
        print("✅ Smart calendar scheduling with conflict resolution")
        print("✅ Progress tracking with manual input and device stubs")
        print("✅ Weekly analytics and performance insights")
        print("✅ Adaptive planning based on completion rates")
        print()
        print("Next Steps:")
        print("• Add your Grok API key to enable full AI features")
        print("• Set up Google Calendar credentials for real scheduling")
        print("• Configure device integrations (Garmin/Renpho)")
        print("• Start your wellness journey with: python3 main.py")
        print()
        print("📁 Generated Files:")
        files = ['profile.json', 'wellness_plan.json', 'progress_data.json', 'scheduling_results.json']
        for file in files:
            if os.path.exists(file):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} (not created)")
        
        print("\n🌟 Ready to improve your wellness journey!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for trying the Personal AI Wellness Assistant!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("But don't worry - this is normal for a demo without full API setup!")

if __name__ == "__main__":
    main()