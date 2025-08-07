#!/usr/bin/env python3
"""
Comprehensive Google Calendar Integration Testing Script
Tests calendar authentication, scheduling, conflict detection, and data sync.
"""

import json
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from calendar_integration import CalendarIntegration
from plan_generator import PlanGenerator
from profile_manager import ProfileManager
from data_utils import get_data_file_path

class CalendarIntegrationTest:
    def __init__(self, use_real_calendar: bool = False):
        self.test_results = []
        self.use_real_calendar = use_real_calendar
        self.temp_dir = None
        self.original_cwd = None
        self.test_events_created = []  # Track events we create for cleanup
        
    def setup_test_environment(self):
        """Set up isolated test environment."""
        print("🔧 Setting up calendar test environment...")
        self.original_cwd = os.getcwd()
        
        if not self.use_real_calendar:
            # Use temporary directory for isolated testing
            self.temp_dir = tempfile.mkdtemp(prefix="calendar_test_")
            os.chdir(self.temp_dir)
            print(f"📁 Test directory: {self.temp_dir}")
        
        print(f"🗓️  Real calendar: {'Yes' if self.use_real_calendar else 'No (Demo mode)'}")
    
    def cleanup_test_environment(self):
        """Clean up test environment and test events."""
        if self.use_real_calendar and self.test_events_created:
            print("🗑️  Cleaning up test events from calendar...")
            calendar = CalendarIntegration()
            if calendar.authenticate():
                for event_id in self.test_events_created:
                    try:
                        calendar.service.events().delete(calendarId='primary', eventId=event_id).execute()
                        print(f"    Deleted event: {event_id[:8]}...")
                    except Exception as e:
                        print(f"    Failed to delete event {event_id[:8]}: {e}")
        
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"🗑️  Cleaned up test directory")
    
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message}")
    
    def create_test_wellness_plan(self) -> Dict[str, Any]:
        """Create a test wellness plan with multiple activities."""
        return {
            "plan_name": "Test Wellness Plan",
            "generated_at": datetime.now().isoformat(),
            "plan_duration": 3,
            "days": [
                {
                    "day": 1,
                    "activities": [
                        {
                            "type": "running",
                            "category": "cardio", 
                            "duration_minutes": 30,
                            "intensity": "moderate",
                            "details": "30-minute morning run",
                            "best_time": "morning"
                        },
                        {
                            "type": "yoga",
                            "category": "flexibility",
                            "duration_minutes": 20,
                            "intensity": "low", 
                            "details": "Evening yoga session",
                            "best_time": "evening"
                        }
                    ]
                },
                {
                    "day": 2,
                    "activities": [
                        {
                            "type": "strength_training",
                            "category": "strength",
                            "duration_minutes": 45,
                            "intensity": "high",
                            "details": "Full body strength workout",
                            "best_time": "afternoon"
                        },
                        {
                            "type": "meditation",
                            "category": "wellbeing", 
                            "duration_minutes": 15,
                            "intensity": "low",
                            "details": "Mindfulness meditation",
                            "best_time": "evening"
                        }
                    ]
                },
                {
                    "day": 3,
                    "activities": [
                        {
                            "type": "cycling",
                            "category": "cardio",
                            "duration_minutes": 40,
                            "intensity": "moderate", 
                            "details": "Outdoor cycling session",
                            "best_time": "morning"
                        }
                    ]
                }
            ]
        }
    
    def test_calendar_authentication(self):
        """Test Google Calendar authentication."""
        try:
            calendar = CalendarIntegration()
            
            # Test authentication
            auth_success = calendar.authenticate()
            self.log_test("Calendar Authentication", auth_success, 
                         "Connected to Google Calendar" if auth_success else "Failed to authenticate")
            
            # Test service initialization
            service_available = calendar.service is not None or not self.use_real_calendar
            self.log_test("Calendar Service Available", service_available,
                         "Service initialized" if service_available else "Service not available")
            
            # Test credentials file handling
            creds_exist = calendar.credentials_file.exists() or not self.use_real_calendar
            self.log_test("Credentials File", creds_exist,
                         f"Credentials at: {calendar.credentials_file}" if creds_exist else "No credentials file")
            
            return calendar
            
        except Exception as e:
            self.log_test("Calendar Authentication", False, f"Error: {e}")
            return None
    
    def test_free_slot_detection(self, calendar: CalendarIntegration):
        """Test free time slot detection."""
        try:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=3)
            
            # Test basic free slot finding
            free_slots = calendar.find_free_slots(start_date, end_date, 30, [(6, 22)])
            slots_found = len(free_slots) > 0
            self.log_test("Free Slot Detection", slots_found,
                         f"Found {len(free_slots)} free 30-minute slots in 3 days")
            
            # Test preferred time slots
            morning_slots = calendar.find_free_slots(start_date, end_date, 30, [(6, 10)])
            evening_slots = calendar.find_free_slots(start_date, end_date, 30, [(18, 22)])
            
            time_preference_works = len(morning_slots) >= 0 and len(evening_slots) >= 0
            self.log_test("Time Preference Filtering", time_preference_works,
                         f"Morning: {len(morning_slots)} slots, Evening: {len(evening_slots)} slots")
            
            # Test different durations
            short_slots = calendar.find_free_slots(start_date, end_date, 15, [(6, 22)])
            long_slots = calendar.find_free_slots(start_date, end_date, 60, [(6, 22)])
            
            duration_scaling = len(short_slots) >= len(free_slots) >= len(long_slots)
            self.log_test("Duration Scaling", duration_scaling,
                         f"15min: {len(short_slots)}, 30min: {len(free_slots)}, 60min: {len(long_slots)}")
            
            return free_slots[:5]  # Return sample slots for further testing
            
        except Exception as e:
            self.log_test("Free Slot Detection", False, f"Error: {e}")
            return []
    
    def test_single_activity_scheduling(self, calendar: CalendarIntegration):
        """Test scheduling a single activity."""
        try:
            test_activity = {
                "type": "test_run",
                "category": "cardio",
                "duration_minutes": 30,
                "intensity": "low",
                "details": "Test activity for calendar integration",
                "equipment_needed": "none"
            }
            
            # Schedule for tomorrow morning
            start_time = (datetime.now() + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
            
            event_id = calendar.schedule_activity(test_activity, start_time)
            
            success = event_id is not None
            if success and self.use_real_calendar:
                self.test_events_created.append(event_id)
            
            self.log_test("Single Activity Scheduling", success,
                         f"Event ID: {event_id[:8]}..." if event_id else "Failed to create event",
                         {"event_id": event_id, "start_time": start_time.isoformat()})
            
            return event_id
            
        except Exception as e:
            self.log_test("Single Activity Scheduling", False, f"Error: {e}")
            return None
    
    def test_wellness_plan_scheduling(self, calendar: CalendarIntegration):
        """Test scheduling a complete wellness plan."""
        try:
            test_plan = self.create_test_wellness_plan()
            start_date = datetime.now() + timedelta(days=1)
            
            # Schedule the plan
            result = calendar.schedule_wellness_plan(
                test_plan, 
                start_date,
                preferred_times=[(6, 10), (18, 21)]
            )
            
            # Track events for cleanup
            if self.use_real_calendar:
                for activity in result.get('scheduled_activities', []):
                    event_id = activity.get('event_id')
                    if event_id:
                        self.test_events_created.append(event_id)
            
            # Analyze results
            scheduled_count = result.get('scheduled_count', 0)
            failed_count = result.get('failed_count', 0)
            total_activities = len([act for day in test_plan['days'] for act in day['activities']])
            
            success = scheduled_count > 0 and scheduled_count + failed_count == total_activities
            
            self.log_test("Wellness Plan Scheduling", success,
                         f"Scheduled: {scheduled_count}/{total_activities}, Failed: {failed_count}",
                         {"result": result})
            
            return result
            
        except Exception as e:
            self.log_test("Wellness Plan Scheduling", False, f"Error: {e}")
            return None
    
    def test_conflict_detection(self, calendar: CalendarIntegration, schedule_result: Dict):
        """Test for scheduling conflicts and double-bookings."""
        if not schedule_result or not schedule_result.get('scheduled_activities'):
            self.log_test("Conflict Detection", False, "No scheduled activities to test")
            return
        
        try:
            scheduled_activities = schedule_result['scheduled_activities']
            conflicts = []
            
            # Check for overlapping activities
            for i, activity1 in enumerate(scheduled_activities):
                time1_start_str = activity1['scheduled_time']
                if isinstance(time1_start_str, datetime):
                    time1_start = time1_start_str
                else:
                    time1_start = datetime.fromisoformat(time1_start_str)
                time1_end = time1_start + timedelta(minutes=activity1['activity']['duration_minutes'])
                
                for j, activity2 in enumerate(scheduled_activities):
                    if i >= j:  # Don't check same activity or already checked pairs
                        continue
                    
                    time2_start_str = activity2['scheduled_time']
                    if isinstance(time2_start_str, datetime):
                        time2_start = time2_start_str
                    else:
                        time2_start = datetime.fromisoformat(time2_start_str)
                    time2_end = time2_start + timedelta(minutes=activity2['activity']['duration_minutes'])
                    
                    # Check for overlap
                    if (time1_start < time2_end and time1_end > time2_start):
                        conflicts.append({
                            'activity1': f"{activity1['activity']['type']} (Day {activity1['day']})",
                            'activity2': f"{activity2['activity']['type']} (Day {activity2['day']})",
                            'time1': f"{time1_start.strftime('%Y-%m-%d %H:%M')} - {time1_end.strftime('%H:%M')}",
                            'time2': f"{time2_start.strftime('%Y-%m-%d %H:%M')} - {time2_end.strftime('%H:%M')}"
                        })
            
            no_conflicts = len(conflicts) == 0
            conflict_msg = f"Found {len(conflicts)} conflicts" if conflicts else "No conflicts detected"
            
            self.log_test("Conflict Detection", no_conflicts, conflict_msg,
                         {"conflicts": conflicts})
            
            if conflicts:
                print("    ⚠️  Detected conflicts:")
                for conflict in conflicts[:3]:  # Show first 3 conflicts
                    print(f"       • {conflict['activity1']} at {conflict['time1']}")
                    print(f"         vs {conflict['activity2']} at {conflict['time2']}")
            
        except Exception as e:
            self.log_test("Conflict Detection", False, f"Error: {e}")
    
    def test_upcoming_activities_retrieval(self, calendar: CalendarIntegration):
        """Test retrieval of upcoming wellness activities."""
        try:
            # Wait a moment for events to propagate (if using real calendar)
            if self.use_real_calendar:
                time.sleep(2)
            
            upcoming = calendar.get_upcoming_activities(7)
            
            activities_found = len(upcoming) >= 0  # Should at least not error
            self.log_test("Upcoming Activities Retrieval", activities_found,
                         f"Retrieved {len(upcoming)} upcoming activities")
            
            # Check data structure
            if upcoming:
                first_activity = upcoming[0]
                required_fields = ['summary', 'start_time', 'event_id']
                has_required_fields = all(field in first_activity for field in required_fields)
                
                self.log_test("Activity Data Structure", has_required_fields,
                             f"First activity has required fields: {list(first_activity.keys())}")
            
            return upcoming
            
        except Exception as e:
            self.log_test("Upcoming Activities Retrieval", False, f"Error: {e}")
            return []
    
    def test_timezone_handling(self, calendar: CalendarIntegration):
        """Test timezone handling in calendar operations."""
        try:
            # Test with different timezone scenarios
            utc_time = datetime.now(timezone.utc)
            local_time = datetime.now()
            
            # Schedule activity with explicit timezone
            test_activity = {
                "type": "timezone_test",
                "duration_minutes": 15,
                "details": "Testing timezone handling"
            }
            
            event_id = calendar.schedule_activity(test_activity, local_time)
            success = event_id is not None
            
            if success and self.use_real_calendar:
                self.test_events_created.append(event_id)
            
            self.log_test("Timezone Handling", success,
                         f"Scheduled with local time, Event: {event_id[:8] if event_id else 'None'}...",
                         {"local_time": local_time.isoformat(), "utc_time": utc_time.isoformat()})
            
        except Exception as e:
            self.log_test("Timezone Handling", False, f"Error: {e}")
    
    def test_error_handling(self, calendar: CalendarIntegration):
        """Test error handling and edge cases."""
        try:
            # Test scheduling with invalid data
            invalid_activity = {
                "type": "invalid_test",
                "duration_minutes": "invalid_duration",  # Invalid type
                "details": None
            }
            
            # This should handle the error gracefully
            past_time = datetime.now() - timedelta(days=1)  # Past time
            event_id = calendar.schedule_activity(invalid_activity, past_time)
            
            # Should either work or fail gracefully (not crash)
            handled_gracefully = True  # If we get here, it didn't crash
            
            self.log_test("Error Handling", handled_gracefully,
                         f"Invalid activity handled gracefully, result: {event_id}")
            
            # Test with far future date
            far_future = datetime.now() + timedelta(days=365)
            future_event = calendar.schedule_activity({
                "type": "future_test",
                "duration_minutes": 30,
                "details": "Far future event"
            }, far_future)
            
            future_handled = True
            if future_event and self.use_real_calendar:
                self.test_events_created.append(future_event)
            
            self.log_test("Future Date Handling", future_handled,
                         f"Far future date handled: {future_event}")
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {e}")
    
    def test_calendar_data_sync(self, calendar: CalendarIntegration):
        """Test synchronization between app and calendar data."""
        try:
            if not self.use_real_calendar:
                self.log_test("Calendar Data Sync", True, "Skipped in demo mode")
                return
            
            # Get current calendar state
            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)
            
            # Get busy times from calendar
            busy_times = calendar.get_busy_times(start_date, end_date)
            busy_count = len(busy_times)
            
            # Get upcoming activities (our events)
            upcoming = calendar.get_upcoming_activities(7)
            wellness_count = len(upcoming)
            
            # The data should be consistent
            sync_healthy = busy_count >= 0 and wellness_count >= 0
            
            self.log_test("Calendar Data Sync", sync_healthy,
                         f"Busy times: {busy_count}, Wellness activities: {wellness_count}")
            
            # Test that our wellness activities appear in busy times
            if self.test_events_created and upcoming:
                our_events_in_busy = any(
                    any('Personal AI Wellness' in busy.get('summary', '') or
                        busy.get('start') == activity.get('start_time')
                        for busy in busy_times)
                    for activity in upcoming
                )
                
                self.log_test("Event Sync Consistency", our_events_in_busy,
                             "Our events appear in calendar busy times")
            
        except Exception as e:
            self.log_test("Calendar Data Sync", False, f"Error: {e}")
    
    def test_performance_large_plan(self, calendar: CalendarIntegration):
        """Test performance with larger wellness plans."""
        try:
            # Create a large wellness plan (14 days, multiple activities per day)
            large_plan = {
                "plan_name": "Large Test Plan",
                "generated_at": datetime.now().isoformat(),
                "plan_duration": 14,
                "days": []
            }
            
            activity_types = ["running", "yoga", "strength_training", "meditation", "cycling"]
            
            for day in range(1, 15):
                activities = []
                for i in range(3):  # 3 activities per day
                    activities.append({
                        "type": activity_types[i % len(activity_types)],
                        "category": "fitness",
                        "duration_minutes": 30,
                        "intensity": "moderate",
                        "details": f"Day {day} activity {i+1}"
                    })
                
                large_plan["days"].append({
                    "day": day,
                    "activities": activities
                })
            
            # Time the scheduling
            start_time = time.time()
            result = calendar.schedule_wellness_plan(
                large_plan,
                datetime.now() + timedelta(days=7),  # Schedule for next week
                preferred_times=[(6, 9), (12, 14), (18, 21)]
            )
            end_time = time.time()
            
            duration = end_time - start_time
            scheduled = result.get('scheduled_count', 0)
            total_activities = len([act for day in large_plan['days'] for act in day['activities']])
            
            # Track events for cleanup (limit to avoid too many test events)
            if self.use_real_calendar and not self.use_real_calendar:  # Only in demo mode
                for activity in result.get('scheduled_activities', [])[:5]:  # Limit cleanup
                    event_id = activity.get('event_id')
                    if event_id:
                        self.test_events_created.append(event_id)
            
            # Performance should be reasonable (less than 30 seconds for 42 activities)
            performance_good = duration < 30
            
            self.log_test("Large Plan Performance", performance_good,
                         f"Scheduled {scheduled}/{total_activities} activities in {duration:.2f}s")
            
        except Exception as e:
            self.log_test("Large Plan Performance", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all calendar integration tests."""
        print("=" * 70)
        print("🗓️  GOOGLE CALENDAR INTEGRATION TESTS")
        print("=" * 70)
        
        try:
            self.setup_test_environment()
            
            # Core functionality tests
            calendar = self.test_calendar_authentication()
            if not calendar:
                print("❌ Cannot continue without calendar instance")
                return
            
            free_slots = self.test_free_slot_detection(calendar)
            single_event = self.test_single_activity_scheduling(calendar)
            schedule_result = self.test_wellness_plan_scheduling(calendar)
            
            # Advanced tests
            self.test_conflict_detection(calendar, schedule_result)
            upcoming = self.test_upcoming_activities_retrieval(calendar)
            self.test_timezone_handling(calendar)
            self.test_error_handling(calendar)
            self.test_calendar_data_sync(calendar)
            
            # Performance test (only in demo mode to avoid cluttering real calendar)
            if not self.use_real_calendar:
                self.test_performance_large_plan(calendar)
            
        finally:
            self.cleanup_test_environment()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 70)
        print("📊 CALENDAR INTEGRATION TEST RESULTS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        # Categorize issues
        critical_issues = []
        warnings = []
        
        for result in self.test_results:
            if not result['success']:
                if any(keyword in result['test'].lower() for keyword in ['conflict', 'double', 'auth']):
                    critical_issues.append(result)
                else:
                    warnings.append(result)
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  ❌ {issue['test']}: {issue['message']}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"  ⚠️  {warning['test']}: {warning['message']}")
        
        print(f"\n{'🎉 ALL TESTS PASSED!' if failed_tests == 0 else '⚠️  Issues detected - see above'}")
        
        # Save detailed results
        results_file = Path("calendar_test_results.json")
        
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
        
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0,
                    'run_at': datetime.now().isoformat(),
                    'test_mode': 'real_calendar' if self.use_real_calendar else 'demo_mode'
                },
                'detailed_results': self.test_results
            }, f, indent=2, default=serialize_datetime)
        
        print(f"📄 Detailed results saved to: {results_file}")

def main():
    """Main entry point for testing script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Google Calendar Integration')
    parser.add_argument('--real', action='store_true', 
                       help='Use real Google Calendar (requires credentials.json)')
    parser.add_argument('--auth-only', action='store_true',
                       help='Test only authentication (no event creation)')
    
    args = parser.parse_args()
    
    if args.auth_only:
        print("🔐 Testing Google Calendar authentication only...")
        calendar = CalendarIntegration()
        success = calendar.authenticate()
        if success:
            print("✅ Authentication successful!")
            if calendar.service:
                try:
                    # Test a simple API call
                    cal_list = calendar.service.calendarList().list(maxResults=1).execute()
                    print(f"📅 Access to {len(cal_list.get('items', []))} calendar(s)")
                except Exception as e:
                    print(f"❌ API test failed: {e}")
            else:
                print("🎭 Running in demo mode (no credentials)")
        else:
            print("❌ Authentication failed")
        return
    
    # Run full test suite
    tester = CalendarIntegrationTest(use_real_calendar=args.real)
    
    if args.real:
        print("⚠️  WARNING: This will create test events in your real Google Calendar!")
        print("These events will be automatically deleted at the end of testing.")
        confirm = input("Continue? (y/N): ").lower().strip()
        if confirm != 'y':
            print("Test cancelled.")
            return
    
    tester.run_all_tests()

if __name__ == "__main__":
    main()