import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from data_utils import get_data_file_path

load_dotenv()

class ProgressTracker:
    def __init__(self, progress_file: str = "progress_data.json"):
        self.progress_file = get_data_file_path(progress_file)
        self.garmin_client_id = os.getenv('GARMIN_CLIENT_ID')
        self.garmin_client_secret = os.getenv('GARMIN_CLIENT_SECRET')
        self.renpho_email = os.getenv('RENPHO_EMAIL')
        self.renpho_password = os.getenv('RENPHO_PASSWORD')
        
    def track_manual_progress(self, wellness_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Manual progress tracking through user input."""
        print("\n=== Daily Progress Check ===")
        
        today = datetime.now().date()
        progress_data = self.load_progress()
        
        if str(today) not in progress_data.get('daily_logs', {}):
            progress_data.setdefault('daily_logs', {})[str(today)] = {
                'date': str(today),
                'completed_activities': [],
                'skipped_activities': [],
                'notes': '',
                'energy_level': None,
                'mood_score': None
            }
        
        today_log = progress_data['daily_logs'][str(today)]
        
        # Get today's planned activities
        plan_day = self._get_plan_for_date(wellness_plan, today)
        if not plan_day:
            print("No activities planned for today.")
            return progress_data
        
        planned_activities = plan_day.get('activities', [])
        print(f"You have {len(planned_activities)} activities planned for today:\n")
        
        # Track each activity
        for i, activity in enumerate(planned_activities, 1):
            activity_name = activity.get('type', 'Activity').replace('_', ' ').title()
            duration = activity.get('duration_minutes', 0)
            intensity = activity.get('intensity', 'moderate')
            
            print(f"{i}. {activity_name} ({duration} min, {intensity} intensity)")
            print(f"   Details: {activity.get('details', 'No details')}")
            
            while True:
                status = input(f"   Status (c)ompleted/(s)kipped/(p)artial: ").lower().strip()
                if status in ['c', 'completed']:
                    completion_notes = input("   Any notes about this activity? (optional): ").strip()
                    today_log['completed_activities'].append({
                        'activity': activity,
                        'completion_time': datetime.now().isoformat(),
                        'notes': completion_notes,
                        'full_completion': True
                    })
                    print("   ✓ Marked as completed!\n")
                    break
                elif status in ['s', 'skipped']:
                    skip_reason = input("   Why did you skip? (optional): ").strip()
                    today_log['skipped_activities'].append({
                        'activity': activity,
                        'skip_reason': skip_reason,
                        'skip_time': datetime.now().isoformat()
                    })
                    print("   ⏭ Marked as skipped.\n")
                    break
                elif status in ['p', 'partial']:
                    partial_duration = input(f"   How many minutes did you complete? (0-{duration}): ").strip()
                    try:
                        partial_duration = int(partial_duration)
                        if 0 <= partial_duration <= duration:
                            completion_notes = input("   Any notes? (optional): ").strip()
                            today_log['completed_activities'].append({
                                'activity': activity,
                                'completion_time': datetime.now().isoformat(),
                                'notes': completion_notes,
                                'full_completion': False,
                                'partial_duration': partial_duration
                            })
                            print(f"   ◐ Marked as partially completed ({partial_duration} min)!\n")
                            break
                        else:
                            print(f"   Please enter a number between 0 and {duration}")
                    except ValueError:
                        print("   Please enter a valid number")
                else:
                    print("   Please enter 'c', 's', or 'p'")
        
        # Overall wellness check
        print("Overall wellness check:")
        
        # Energy level
        while True:
            try:
                energy = int(input("Energy level today (1-10, 1=exhausted, 10=energetic): "))
                if 1 <= energy <= 10:
                    today_log['energy_level'] = energy
                    break
                print("Please enter a number between 1 and 10")
            except ValueError:
                print("Please enter a valid number")
        
        # Mood score
        while True:
            try:
                mood = int(input("Mood score today (1-10, 1=terrible, 10=excellent): "))
                if 1 <= mood <= 10:
                    today_log['mood_score'] = mood
                    break
                print("Please enter a number between 1 and 10")
            except ValueError:
                print("Please enter a valid number")
        
        # General notes
        general_notes = input("Any other notes about today? (optional): ").strip()
        today_log['notes'] = general_notes
        
        # Save progress
        self.save_progress(progress_data)
        
        # Calculate and display summary
        summary = self._calculate_daily_summary(today_log)
        self._display_progress_summary(summary)
        
        return progress_data
    
    def get_garmin_data(self, days_back: int = 7) -> Dict[str, Any]:
        """Fetch data from Garmin (stubbed - requires OAuth setup)."""
        if not self.garmin_client_id:
            print("Garmin credentials not configured. Using manual input...")
            return self._get_manual_device_data("Garmin")
        
        # This is a stub implementation
        print("Garmin API integration not fully implemented. Using sample data...")
        
        # In a real implementation, you would:
        # 1. Use OAuth to get user authorization
        # 2. Make requests to Garmin Health API endpoints
        # 3. Parse the response data
        
        sample_data = {
            'steps': 8500,
            'heart_rate_avg': 75,
            'heart_rate_resting': 65,
            'calories_burned': 2200,
            'active_minutes': 45,
            'distance_km': 6.2,
            'sleep_hours': 7.5,
            'data_date': datetime.now().date().isoformat(),
            'source': 'garmin_stub'
        }
        
        return sample_data
    
    def get_renpho_data(self, days_back: int = 7) -> Dict[str, Any]:
        """Fetch data from Renpho scale (stubbed - requires reverse engineering)."""
        if not self.renpho_email:
            print("Renpho credentials not configured. Using manual input...")
            return self._get_manual_device_data("Renpho")
        
        # This is a stub implementation
        print("Renpho API integration not fully implemented. Using sample data...")
        
        # In a real implementation, you would:
        # 1. POST to https://api.renpho.com/v1/auth/login with email/password
        # 2. Extract auth token from response
        # 3. Use token to fetch measurements from /v1/measurements
        
        sample_data = {
            'weight_kg': 70.5,
            'body_fat_percent': 15.2,
            'muscle_mass_kg': 55.8,
            'bone_mass_kg': 3.2,
            'water_percent': 58.7,
            'bmr_calories': 1650,
            'measurement_date': datetime.now().date().isoformat(),
            'source': 'renpho_stub'
        }
        
        return sample_data
    
    def _get_manual_device_data(self, device_type: str) -> Dict[str, Any]:
        """Get device data through manual input."""
        print(f"\n=== Manual {device_type} Data Entry ===")
        data = {
            'data_date': datetime.now().date().isoformat(),
            'source': f'{device_type.lower()}_manual'
        }
        
        if device_type.lower() == 'garmin':
            try:
                data['steps'] = int(input("Steps today (or 0 to skip): ") or "0")
                data['heart_rate_avg'] = int(input("Average heart rate (or 0 to skip): ") or "0")
                data['active_minutes'] = int(input("Active minutes (or 0 to skip): ") or "0")
                data['sleep_hours'] = float(input("Hours of sleep last night (or 0 to skip): ") or "0")
            except ValueError:
                print("Invalid input, using defaults")
                
        elif device_type.lower() == 'renpho':
            try:
                data['weight_kg'] = float(input("Current weight in kg (or 0 to skip): ") or "0")
                data['body_fat_percent'] = float(input("Body fat percentage (or 0 to skip): ") or "0")
            except ValueError:
                print("Invalid input, using defaults")
        
        return data
    
    def calculate_weekly_progress(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weekly progress statistics."""
        daily_logs = progress_data.get('daily_logs', {})
        
        # Get last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
        
        week_logs = []
        date = start_date
        while date <= end_date:
            if str(date) in daily_logs:
                week_logs.append(daily_logs[str(date)])
            date += timedelta(days=1)
        
        if not week_logs:
            return {'period': 'No data available', 'stats': {}}
        
        # Calculate statistics
        total_activities = 0
        completed_activities = 0
        total_duration = 0
        completed_duration = 0
        energy_scores = []
        mood_scores = []
        
        for day_log in week_logs:
            # Count activities
            day_completed = len(day_log.get('completed_activities', []))
            day_skipped = len(day_log.get('skipped_activities', []))
            day_total = day_completed + day_skipped
            
            total_activities += day_total
            completed_activities += day_completed
            
            # Calculate duration
            for activity in day_log.get('completed_activities', []):
                if activity.get('full_completion', True):
                    total_duration += activity['activity'].get('duration_minutes', 0)
                    completed_duration += activity['activity'].get('duration_minutes', 0)
                else:
                    total_duration += activity['activity'].get('duration_minutes', 0)
                    completed_duration += activity.get('partial_duration', 0)
            
            # Collect wellness scores
            if day_log.get('energy_level'):
                energy_scores.append(day_log['energy_level'])
            if day_log.get('mood_score'):
                mood_scores.append(day_log['mood_score'])
        
        # Calculate rates and averages
        completion_rate = completed_activities / total_activities if total_activities > 0 else 0
        duration_completion_rate = completed_duration / total_duration if total_duration > 0 else 0
        avg_energy = sum(energy_scores) / len(energy_scores) if energy_scores else 0
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
        
        return {
            'period': f"{start_date} to {end_date}",
            'days_with_data': len(week_logs),
            'stats': {
                'activity_completion_rate': completion_rate,
                'duration_completion_rate': duration_completion_rate,
                'total_activities_planned': total_activities,
                'total_activities_completed': completed_activities,
                'total_duration_planned_minutes': total_duration,
                'total_duration_completed_minutes': completed_duration,
                'average_energy_level': avg_energy,
                'average_mood_score': avg_mood,
                'active_days': len([log for log in week_logs if log.get('completed_activities')])
            }
        }
    
    def should_adapt_plan(self, progress_data: Dict[str, Any]) -> bool:
        """Determine if the plan should be adapted based on progress."""
        weekly_stats = self.calculate_weekly_progress(progress_data)
        stats = weekly_stats.get('stats', {})
        
        completion_rate = stats.get('activity_completion_rate', 1.0)
        avg_energy = stats.get('average_energy_level', 5)
        active_days = stats.get('active_days', 0)
        
        # Adapt if completion rate is too low or too high
        if completion_rate < 0.5:
            return True
        if completion_rate > 0.95 and avg_energy > 7:
            return True
        if active_days < 3:  # Less than 3 active days in a week
            return True
            
        return False
    
    def _get_plan_for_date(self, wellness_plan: Dict[str, Any], target_date) -> Optional[Dict[str, Any]]:
        """Get the planned activities for a specific date."""
        plan_start = wellness_plan.get('generated_at')
        if not plan_start:
            return None
        
        plan_start_date = datetime.fromisoformat(plan_start).date()
        days_diff = (target_date - plan_start_date).days
        
        # Find the day in the plan
        for day in wellness_plan.get('days', []):
            if day.get('day', 1) == days_diff + 1:
                return day
        
        return None
    
    def _calculate_daily_summary(self, day_log: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for a single day."""
        completed = len(day_log.get('completed_activities', []))
        skipped = len(day_log.get('skipped_activities', []))
        total = completed + skipped
        
        completion_rate = completed / total if total > 0 else 0
        
        total_minutes = sum(
            act.get('partial_duration', act['activity'].get('duration_minutes', 0))
            for act in day_log.get('completed_activities', [])
        )
        
        return {
            'completion_rate': completion_rate,
            'activities_completed': completed,
            'activities_skipped': skipped,
            'total_activities': total,
            'total_active_minutes': total_minutes,
            'energy_level': day_log.get('energy_level'),
            'mood_score': day_log.get('mood_score')
        }
    
    def _display_progress_summary(self, summary: Dict[str, Any]) -> None:
        """Display a daily progress summary."""
        print(f"\n=== Today's Progress Summary ===")
        print(f"Completion Rate: {summary['completion_rate']:.1%}")
        print(f"Activities: {summary['activities_completed']} completed, {summary['activities_skipped']} skipped")
        print(f"Active Time: {summary['total_active_minutes']} minutes")
        print(f"Energy Level: {summary['energy_level']}/10")
        print(f"Mood Score: {summary['mood_score']}/10")
        
        # Motivational message
        if summary['completion_rate'] >= 0.8:
            print("🎉 Excellent work today! Keep it up!")
        elif summary['completion_rate'] >= 0.5:
            print("👍 Good effort today! Every step counts.")
        else:
            print("💪 Tomorrow is a new opportunity. You've got this!")
    
    def load_progress(self) -> Dict[str, Any]:
        """Load progress data from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            'daily_logs': {},
            'device_data': {},
            'weekly_summaries': {}
        }
    
    def save_progress(self, progress_data: Dict[str, Any]) -> None:
        """Save progress data to file."""
        progress_data['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2, default=str)
    
    def display_weekly_report(self, progress_data: Dict[str, Any]) -> None:
        """Display a comprehensive weekly progress report."""
        weekly_stats = self.calculate_weekly_progress(progress_data)
        
        print(f"\n=== Weekly Progress Report ===")
        print(f"Period: {weekly_stats['period']}")
        print(f"Days with data: {weekly_stats['days_with_data']}/7\n")
        
        stats = weekly_stats.get('stats', {})
        
        print("Activity Performance:")
        print(f"  Completion Rate: {stats.get('activity_completion_rate', 0):.1%}")
        print(f"  Duration Completion: {stats.get('duration_completion_rate', 0):.1%}")
        print(f"  Activities Completed: {stats.get('total_activities_completed', 0)}/{stats.get('total_activities_planned', 0)}")
        print(f"  Active Days: {stats.get('active_days', 0)}/7")
        print(f"  Total Active Time: {stats.get('total_duration_completed_minutes', 0)} minutes\n")
        
        print("Wellness Scores:")
        print(f"  Average Energy Level: {stats.get('average_energy_level', 0):.1f}/10")
        print(f"  Average Mood Score: {stats.get('average_mood_score', 0):.1f}/10\n")
        
        # Recommendations
        completion_rate = stats.get('activity_completion_rate', 0)
        if completion_rate < 0.5:
            print("💡 Recommendation: Consider reducing activity intensity or duration")
        elif completion_rate > 0.9:
            print("💡 Recommendation: You're crushing it! Consider adding more challenging activities")
        else:
            print("💡 Recommendation: Keep up the great work! You're in a good rhythm")

if __name__ == "__main__":
    tracker = ProgressTracker()
    
    # Test progress tracking
    sample_plan = {
        "generated_at": datetime.now().isoformat(),
        "days": [
            {
                "day": 1,
                "activities": [
                    {
                        "type": "running",
                        "duration_minutes": 30,
                        "intensity": "moderate",
                        "details": "30-minute easy run"
                    },
                    {
                        "type": "meditation",
                        "duration_minutes": 10,
                        "intensity": "low",
                        "details": "10-minute breathing exercise"
                    }
                ]
            }
        ]
    }
    
    progress_data = tracker.track_manual_progress(sample_plan)
    tracker.display_weekly_report(progress_data)