import os
import json
import pickle
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarIntegration:
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        if not os.path.exists(self.credentials_file):
            print("⚠️  Google Calendar credentials not found - using demo mode")
            print("📅 Calendar features will show mock scheduling results")
            self.service = None
            return True  # Return True for demo mode
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    print("⚠️  Continuing in demo mode without calendar integration")
                    self.service = None
                    return True
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building calendar service: {e}")
            print("⚠️  Continuing in demo mode without calendar integration")
            self.service = None
            return True
    
    def get_busy_times(self, start_date: datetime, end_date: datetime, calendar_id: str = 'primary') -> List[Dict[str, Any]]:
        """Get busy time slots from calendar."""
        if not self.service:
            # Return mock busy times for demo
            return [
                {
                    'summary': 'Meeting',
                    'start': start_date.replace(hour=9, minute=0),
                    'end': start_date.replace(hour=10, minute=0)
                },
                {
                    'summary': 'Lunch',
                    'start': start_date.replace(hour=12, minute=0),
                    'end': start_date.replace(hour=13, minute=0)
                }
            ]
        
        try:
            # Convert to RFC3339 format
            time_min = start_date.isoformat()
            time_max = end_date.isoformat()
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=100
            ).execute()
            
            events = events_result.get('items', [])
            busy_times = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Skip all-day events for now
                if 'T' not in start:
                    continue
                
                busy_times.append({
                    'summary': event.get('summary', 'Busy'),
                    'start': datetime.fromisoformat(start.replace('Z', '+00:00')),
                    'end': datetime.fromisoformat(end.replace('Z', '+00:00'))
                })
            
            return busy_times
            
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
    
    def find_free_slots(self, start_date: datetime, end_date: datetime, 
                       slot_duration_minutes: int, preferred_times: List[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
        """Find available time slots for activities."""
        if preferred_times is None:
            preferred_times = [(6, 22)]  # 6 AM to 10 PM by default
        
        busy_times = self.get_busy_times(start_date, end_date)
        free_slots = []
        
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_date < end_date:
            # Check each preferred time range for this day
            for start_hour, end_hour in preferred_times:
                day_start = current_date.replace(hour=start_hour)
                day_end = current_date.replace(hour=end_hour)
                
                # Find free slots within this time range
                current_time = day_start
                
                while current_time + timedelta(minutes=slot_duration_minutes) <= day_end:
                    slot_end = current_time + timedelta(minutes=slot_duration_minutes)
                    
                    # Check if this slot conflicts with any busy time
                    is_free = True
                    for busy in busy_times:
                        if (current_time < busy['end'] and slot_end > busy['start']):
                            is_free = False
                            # Jump to end of busy period
                            current_time = busy['end']
                            break
                    
                    if is_free:
                        free_slots.append({
                            'start': current_time,
                            'end': slot_end,
                            'duration_minutes': slot_duration_minutes,
                            'date': current_date.date()
                        })
                        current_time += timedelta(minutes=15)  # Move in 15-minute increments
                    
            current_date += timedelta(days=1)
        
        return free_slots
    
    def schedule_activity(self, activity: Dict[str, Any], start_time: datetime, calendar_id: str = 'primary') -> Optional[str]:
        """Schedule a single activity on the calendar."""
        if not self.service:
            # Return mock event ID for demo
            return f"demo_event_{activity.get('type', 'activity')}_{int(start_time.timestamp())}"
        
        duration_minutes = activity.get('duration_minutes', 30)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create event description
        details_parts = []
        if activity.get('details'):
            details_parts.append(activity['details'])
        if activity.get('intensity'):
            details_parts.append(f"Intensity: {activity['intensity']}")
        if activity.get('equipment_needed') and activity['equipment_needed'] != 'none':
            details_parts.append(f"Equipment: {activity['equipment_needed']}")
        
        description = '\n'.join(details_parts)
        description += f"\n\nGenerated by Personal AI Wellness Assistant"
        
        event = {
            'summary': f"🏃‍♂️ {activity.get('type', 'Activity').replace('_', ' ').title()}",
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': True,
            },
            'colorId': '2'  # Green color for wellness activities
        }
        
        try:
            created_event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return created_event.get('id')
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None
    
    def schedule_wellness_plan(self, wellness_plan: Dict[str, Any], 
                              start_date: datetime = None, preferred_times: List[Tuple[int, int]] = None) -> Dict[str, Any]:
        """Schedule all activities from a wellness plan."""
        if start_date is None:
            start_date = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        if preferred_times is None:
            # Default preferred times: 6-9 AM and 6-9 PM
            preferred_times = [(6, 9), (18, 21)]
        
        scheduled_activities = []
        failed_activities = []
        
        plan_days = wellness_plan.get('days', [])
        
        for day_data in plan_days:
            day_number = day_data.get('day', 1)
            day_date = start_date + timedelta(days=day_number - 1)
            
            activities = day_data.get('activities', [])
            
            for activity in activities:
                duration = activity.get('duration_minutes', 30)
                
                # Find free slots for this day
                day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                free_slots = self.find_free_slots(day_start, day_end, duration, preferred_times)
                
                if free_slots:
                    # Choose best time based on activity type and user preferences
                    best_slot = self._choose_best_slot(activity, free_slots)
                    
                    event_id = self.schedule_activity(activity, best_slot['start'])
                    
                    if event_id:
                        scheduled_activities.append({
                            'activity': activity,
                            'scheduled_time': best_slot['start'],
                            'event_id': event_id,
                            'day': day_number
                        })
                    else:
                        failed_activities.append({
                            'activity': activity,
                            'reason': 'Failed to create calendar event',
                            'day': day_number
                        })
                else:
                    failed_activities.append({
                        'activity': activity,
                        'reason': 'No available time slots found',
                        'day': day_number
                    })
        
        result = {
            'scheduled_count': len(scheduled_activities),
            'failed_count': len(failed_activities),
            'scheduled_activities': scheduled_activities,
            'failed_activities': failed_activities,
            'start_date': start_date.isoformat()
        }
        
        # Save scheduling results
        with open('scheduling_results.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def _choose_best_slot(self, activity: Dict[str, Any], free_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Choose the best time slot for an activity based on type and preferences."""
        activity_type = activity.get('type', '').lower()
        category = activity.get('category', '').lower()
        best_time = activity.get('best_time', '').lower()
        
        # Score slots based on activity type
        scored_slots = []
        
        for slot in free_slots:
            hour = slot['start'].hour
            score = 0
            
            # Morning activities (6-10 AM)
            if hour >= 6 and hour <= 10:
                if activity_type in ['running', 'cycling', 'cardio'] or category == 'cardio':
                    score += 10
                if best_time in ['morning', 'early morning']:
                    score += 15
            
            # Afternoon activities (12-17)
            elif hour >= 12 and hour <= 17:
                if activity_type in ['strength_training', 'yoga'] or category in ['strength', 'flexibility']:
                    score += 8
                if best_time in ['afternoon', 'midday']:
                    score += 15
            
            # Evening activities (18-21)
            elif hour >= 18 and hour <= 21:
                if activity_type in ['yoga', 'meditation', 'stretching'] or category in ['wellbeing', 'flexibility']:
                    score += 12
                if best_time in ['evening', 'night']:
                    score += 15
            
            # Avoid very early or very late times
            if hour < 6 or hour > 22:
                score -= 10
            
            scored_slots.append((score, slot))
        
        # Return the highest scored slot
        if scored_slots:
            scored_slots.sort(key=lambda x: x[0], reverse=True)
            return scored_slots[0][1]
        
        return free_slots[0] if free_slots else None
    
    def get_upcoming_activities(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming wellness activities from calendar."""
        if not self.service:
            # Return mock upcoming activities for demo
            start_time = datetime.now() + timedelta(hours=2)
            return [
                {
                    'summary': '🏃‍♂️ Morning Run',
                    'start_time': start_time,
                    'description': '30-minute easy-paced run',
                    'event_id': 'demo_event_1'
                },
                {
                    'summary': '🧘‍♀️ Evening Meditation',
                    'start_time': start_time + timedelta(hours=10),
                    'description': '15-minute mindfulness session',
                    'event_id': 'demo_event_2'
                }
            ]
        
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days_ahead)
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                q='Personal AI Wellness Assistant'  # Filter for our events
            ).execute()
            
            events = events_result.get('items', [])
            activities = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                if 'T' in start:  # Skip all-day events
                    activities.append({
                        'summary': event.get('summary', ''),
                        'start_time': datetime.fromisoformat(start.replace('Z', '+00:00')),
                        'description': event.get('description', ''),
                        'event_id': event.get('id')
                    })
            
            return activities
            
        except Exception as e:
            print(f"Error fetching upcoming activities: {e}")
            return []
    
    def display_schedule_summary(self, schedule_result: Dict[str, Any]) -> None:
        """Display a summary of the scheduling results."""
        print(f"\n=== Scheduling Summary ===")
        print(f"Successfully scheduled: {schedule_result['scheduled_count']} activities")
        print(f"Failed to schedule: {schedule_result['failed_count']} activities")
        print(f"Plan start date: {schedule_result['start_date'][:10]}\n")
        
        if schedule_result['scheduled_activities']:
            print("Scheduled Activities:")
            for item in schedule_result['scheduled_activities'][:5]:  # Show first 5
                activity = item['activity']
                time = item['scheduled_time']
                if isinstance(time, str):
                    time = datetime.fromisoformat(time)
                
                print(f"  Day {item['day']}: {activity['type'].replace('_', ' ').title()}")
                print(f"    Time: {time.strftime('%a %b %d, %I:%M %p')}")
                print(f"    Duration: {activity.get('duration_minutes', 0)} minutes\n")
        
        if schedule_result['failed_activities']:
            print("Failed to Schedule:")
            for item in schedule_result['failed_activities']:
                activity = item['activity']
                print(f"  Day {item['day']}: {activity['type'].replace('_', ' ').title()}")
                print(f"    Reason: {item['reason']}\n")

if __name__ == "__main__":
    # Test calendar integration
    calendar = CalendarIntegration()
    
    if calendar.authenticate():
        print("Calendar authentication successful!")
        
        # Test finding free slots
        start = datetime.now()
        end = start + timedelta(days=7)
        
        free_slots = calendar.find_free_slots(start, end, 30, [(6, 10), (18, 21)])
        print(f"Found {len(free_slots)} free 30-minute slots in the next 7 days")
        
        # Show first few slots
        for slot in free_slots[:5]:
            print(f"  {slot['start'].strftime('%a %b %d, %I:%M %p')} - {slot['end'].strftime('%I:%M %p')}")
    else:
        print("Calendar authentication failed. Please check your credentials.json file.")