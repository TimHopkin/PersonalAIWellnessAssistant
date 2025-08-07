#!/usr/bin/env python3
"""
Calendar Integration Monitor
Real-time monitoring of calendar operations and health.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from calendar_integration import CalendarIntegration
from plan_generator import PlanGenerator

class CalendarMonitor:
    def __init__(self):
        self.calendar = CalendarIntegration()
        self.plan_generator = PlanGenerator()
        self.monitoring_data = []
        
    def check_calendar_health(self) -> Dict[str, Any]:
        """Check overall calendar integration health."""
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'authentication_status': 'unknown',
            'service_available': False,
            'upcoming_events_count': 0,
            'conflicts_detected': 0,
            'errors': []
        }
        
        try:
            # Test authentication
            auth_success = self.calendar.authenticate()
            health_data['authentication_status'] = 'success' if auth_success else 'failed'
            health_data['service_available'] = self.calendar.service is not None
            
            if self.calendar.service:
                # Test basic API call
                try:
                    cal_list = self.calendar.service.calendarList().list(maxResults=1).execute()
                    health_data['api_test'] = 'success'
                except Exception as e:
                    health_data['api_test'] = 'failed'
                    health_data['errors'].append(f'API test failed: {e}')
                
                # Get upcoming events
                try:
                    upcoming = self.calendar.get_upcoming_activities(7)
                    health_data['upcoming_events_count'] = len(upcoming)
                except Exception as e:
                    health_data['errors'].append(f'Failed to get upcoming events: {e}')
                
                # Check for conflicts in existing events
                conflicts = self.detect_existing_conflicts()
                health_data['conflicts_detected'] = len(conflicts)
                health_data['conflicts'] = conflicts[:3]  # Show first 3
            
        except Exception as e:
            health_data['errors'].append(f'Health check error: {e}')
        
        return health_data
    
    def detect_existing_conflicts(self) -> List[Dict[str, Any]]:
        """Detect conflicts in existing wellness events."""
        conflicts = []
        
        try:
            # Get existing wellness events for the next 2 weeks
            start_date = datetime.now()
            end_date = start_date + timedelta(days=14)
            
            existing_events = self.calendar._get_existing_wellness_events(start_date, end_date)
            
            # Check for overlapping events
            for i, event1 in enumerate(existing_events):
                for j, event2 in enumerate(existing_events):
                    if i >= j:
                        continue
                    
                    # Check for overlap
                    if (event1['start'] < event2['end'] and event1['end'] > event2['start']):
                        conflicts.append({
                            'event1': {
                                'summary': event1['summary'],
                                'start': event1['start'].isoformat(),
                                'end': event1['end'].isoformat()
                            },
                            'event2': {
                                'summary': event2['summary'],
                                'start': event2['start'].isoformat(),
                                'end': event2['end'].isoformat()
                            },
                            'overlap_minutes': min(event1['end'], event2['end']) - max(event1['start'], event2['start'])
                        })
        
        except Exception as e:
            print(f"Error detecting conflicts: {e}")
        
        return conflicts
    
    def validate_calendar_sync(self) -> Dict[str, Any]:
        """Validate that app data matches calendar data."""
        validation_data = {
            'timestamp': datetime.now().isoformat(),
            'app_events_count': 0,
            'calendar_events_count': 0,
            'sync_status': 'unknown',
            'mismatches': []
        }
        
        try:
            # Load scheduling results from app
            results_file = Path('scheduling_results.json')
            if results_file.exists():
                with open(results_file, 'r') as f:
                    app_schedule = json.load(f)
                validation_data['app_events_count'] = app_schedule.get('scheduled_count', 0)
            
            # Get events from calendar
            if self.calendar.service:
                start_date = datetime.now() - timedelta(days=7)
                end_date = datetime.now() + timedelta(days=14)
                calendar_events = self.calendar._get_existing_wellness_events(start_date, end_date)
                validation_data['calendar_events_count'] = len(calendar_events)
                
                # Compare counts
                if validation_data['app_events_count'] == validation_data['calendar_events_count']:
                    validation_data['sync_status'] = 'synchronized'
                else:
                    validation_data['sync_status'] = 'out_of_sync'
                    validation_data['mismatches'].append(
                        f"Count mismatch: App has {validation_data['app_events_count']}, "
                        f"Calendar has {validation_data['calendar_events_count']}"
                    )
        
        except Exception as e:
            validation_data['sync_status'] = 'error'
            validation_data['mismatches'].append(f'Validation error: {e}')
        
        return validation_data
    
    def analyze_scheduling_patterns(self) -> Dict[str, Any]:
        """Analyze scheduling patterns and success rates."""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_attempts': 0,
            'success_rate': 0,
            'common_failure_reasons': [],
            'time_slot_distribution': {},
            'activity_type_distribution': {}
        }
        
        try:
            results_file = Path('scheduling_results.json')
            if results_file.exists():
                with open(results_file, 'r') as f:
                    schedule_data = json.load(f)
                
                scheduled = schedule_data.get('scheduled_activities', [])
                failed = schedule_data.get('failed_activities', [])
                
                analysis['total_attempts'] = len(scheduled) + len(failed)
                if analysis['total_attempts'] > 0:
                    analysis['success_rate'] = len(scheduled) / analysis['total_attempts'] * 100
                
                # Analyze failure reasons
                failure_reasons = {}
                for failure in failed:
                    reason = failure.get('reason', 'Unknown')
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                
                analysis['common_failure_reasons'] = [
                    {'reason': reason, 'count': count} 
                    for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)
                ]
                
                # Analyze time slot distribution
                time_slots = {}
                for activity in scheduled:
                    time_str = activity.get('scheduled_time', '')
                    if time_str:
                        try:
                            dt = datetime.fromisoformat(time_str)
                            hour = dt.hour
                            time_period = 'Morning' if 6 <= hour < 12 else 'Afternoon' if 12 <= hour < 18 else 'Evening'
                            time_slots[time_period] = time_slots.get(time_period, 0) + 1
                        except:
                            pass
                
                analysis['time_slot_distribution'] = time_slots
                
                # Analyze activity types
                activity_types = {}
                for activity in scheduled:
                    activity_type = activity.get('activity', {}).get('type', 'Unknown')
                    activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
                
                analysis['activity_type_distribution'] = activity_types
        
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def generate_report(self) -> str:
        """Generate a comprehensive calendar integration report."""
        print("🗓️  Generating Calendar Integration Report...")
        print("=" * 60)
        
        # Health check
        health = self.check_calendar_health()
        print(f"📊 Calendar Health Status:")
        print(f"   Authentication: {health['authentication_status']}")
        print(f"   Service Available: {health['service_available']}")
        print(f"   Upcoming Events: {health['upcoming_events_count']}")
        print(f"   Conflicts Detected: {health['conflicts_detected']}")
        
        if health['errors']:
            print(f"   Errors: {len(health['errors'])}")
            for error in health['errors'][:3]:
                print(f"      • {error}")
        
        print()
        
        # Sync validation
        sync = self.validate_calendar_sync()
        print(f"🔄 Calendar Sync Status:")
        print(f"   Status: {sync['sync_status']}")
        print(f"   App Events: {sync['app_events_count']}")
        print(f"   Calendar Events: {sync['calendar_events_count']}")
        
        if sync['mismatches']:
            print(f"   Issues:")
            for issue in sync['mismatches']:
                print(f"      • {issue}")
        
        print()
        
        # Scheduling analysis
        analysis = self.analyze_scheduling_patterns()
        print(f"📈 Scheduling Analysis:")
        print(f"   Total Scheduling Attempts: {analysis['total_attempts']}")
        print(f"   Success Rate: {analysis['success_rate']:.1f}%")
        
        if analysis['common_failure_reasons']:
            print(f"   Common Failures:")
            for failure in analysis['common_failure_reasons'][:3]:
                print(f"      • {failure['reason']}: {failure['count']} times")
        
        if analysis['time_slot_distribution']:
            print(f"   Time Distribution:")
            for period, count in analysis['time_slot_distribution'].items():
                print(f"      • {period}: {count} activities")
        
        print()
        
        # Conflicts
        if health['conflicts_detected'] > 0:
            print(f"⚠️  Detected Conflicts ({health['conflicts_detected']}):")
            for conflict in health.get('conflicts', []):
                event1_time = conflict['event1']['start'][:16].replace('T', ' ')
                event2_time = conflict['event2']['start'][:16].replace('T', ' ')
                print(f"   • {conflict['event1']['summary']} at {event1_time}")
                print(f"     vs {conflict['event2']['summary']} at {event2_time}")
        
        # Recommendations
        print(f"💡 Recommendations:")
        recommendations = []
        
        if health['authentication_status'] != 'success':
            recommendations.append("Fix calendar authentication issues")
        
        if health['conflicts_detected'] > 0:
            recommendations.append("Resolve scheduling conflicts to avoid double-booking")
        
        if sync['sync_status'] == 'out_of_sync':
            recommendations.append("Synchronize app data with calendar events")
        
        if analysis['success_rate'] < 80:
            recommendations.append("Improve scheduling success rate by analyzing failure reasons")
        
        if not recommendations:
            recommendations.append("Calendar integration appears healthy!")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Save report
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'health': health,
            'sync_validation': sync,
            'scheduling_analysis': analysis,
            'recommendations': recommendations
        }
        
        report_file = Path('calendar_integration_report.json')
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return str(report_file)
    
    def continuous_monitoring(self, interval_minutes: int = 30):
        """Run continuous monitoring of calendar integration."""
        print(f"👁️  Starting continuous calendar monitoring (every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                health = self.check_calendar_health()
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                status = "✅" if health['authentication_status'] == 'success' else "❌"
                conflicts = f", {health['conflicts_detected']} conflicts" if health['conflicts_detected'] > 0 else ""
                
                print(f"[{timestamp}] {status} Auth: {health['authentication_status']}, "
                      f"Events: {health['upcoming_events_count']}{conflicts}")
                
                if health['errors']:
                    for error in health['errors']:
                        print(f"    ⚠️  {error}")
                
                self.monitoring_data.append(health)
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Monitoring stopped")
            print(f"📊 Collected {len(self.monitoring_data)} health checks")
            
            # Save monitoring data
            monitor_file = Path('calendar_monitoring_data.json')
            with open(monitor_file, 'w') as f:
                json.dump(self.monitoring_data, f, indent=2, default=str)
            
            print(f"📄 Monitoring data saved to: {monitor_file}")

def main():
    """Main entry point for calendar monitoring."""
    import sys
    
    monitor = CalendarMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--report':
            monitor.generate_report()
        elif sys.argv[1] == '--health':
            health = monitor.check_calendar_health()
            print("🔍 Quick Health Check:")
            print(f"   Status: {health['authentication_status']}")
            print(f"   Events: {health['upcoming_events_count']}")
            print(f"   Conflicts: {health['conflicts_detected']}")
        elif sys.argv[1] == '--conflicts':
            conflicts = monitor.detect_existing_conflicts()
            if conflicts:
                print(f"⚠️  Found {len(conflicts)} conflicts:")
                for conflict in conflicts:
                    print(f"   • {conflict['event1']['summary']} overlaps with {conflict['event2']['summary']}")
            else:
                print("✅ No conflicts detected")
        elif sys.argv[1] == '--monitor':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            monitor.continuous_monitoring(interval)
        else:
            print("Usage: python3 monitor_calendar.py [--report|--health|--conflicts|--monitor [interval]]")
    else:
        monitor.generate_report()

if __name__ == "__main__":
    main()