import os
import json
import pickle
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple, Set
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
try:
    from .data_utils import get_data_file_path
except ImportError:
    from data_utils import get_data_file_path

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarIntegration:
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        self.credentials_file = get_data_file_path(credentials_file)
        self.token_file = get_data_file_path(token_file)
        self.service = None
        
    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        print(f"🔍 Looking for credentials at: {self.credentials_file}")
        if not self.credentials_file.exists():
            print("⚠️  Google Calendar credentials not found - using demo mode")
            print("📅 Calendar features will show mock scheduling results")
            self.service = None
            return True  # Return True for demo mode
        
        creds = None
        
        # Load existing token
        if self.token_file.exists():
            print(f"🔍 Found existing token file: {self.token_file}")
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                print("✅ Successfully loaded existing authentication token")
            except Exception as e:
                print(f"❌ Failed to load token file: {e}")
                creds = None
        else:
            print(f"🔍 No existing token file found at: {self.token_file}")
        
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
                    print("🔐 Starting OAuth2 authentication flow...")
                    print("🌐 A browser window should open for Google login...")
                    flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), SCOPES)
                    creds = flow.run_local_server(port=0)
                    print("✅ OAuth2 authentication completed successfully!")
                except Exception as e:
                    print(f"❌ Error during authentication: {e}")
                    print("⚠️  Continuing in demo mode without calendar integration")
                    self.service = None
                    return True
            
            # Save credentials for future use
            try:
                print(f"💾 Saving authentication token to: {self.token_file}")
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"✅ Token saved successfully! File exists: {self.token_file.exists()}")
            except Exception as e:
                print(f"❌ Failed to save token: {e}")
                print(f"Token file path: {self.token_file}")
                print(f"Parent directory exists: {self.token_file.parent.exists()}")
                print(f"Parent directory writable: {os.access(self.token_file.parent, os.W_OK)}")
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("🗓️  Google Calendar service initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error building calendar service: {e}")
            print("⚠️  Continuing in demo mode without calendar integration")
            self.service = None
            return True
    
    def clear_authentication(self):
        """Clear existing authentication tokens to force re-authentication."""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
                print(f"🗑️  Cleared authentication token: {self.token_file}")
            self.service = None
            return True
        except Exception as e:
            print(f"❌ Failed to clear authentication: {e}")
            return False
    
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
            # Ensure datetime has timezone info for API call
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            
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
        
        # Use local timezone instead of UTC
        import time
        local_tz = time.tzname[0] if not time.daylight else time.tzname[1]
        
        event = {
            'summary': f"🏃‍♂️ {activity.get('type', 'Activity').replace('_', ' ').title()}",
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': local_tz,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': local_tz,
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
        """Schedule all activities from a wellness plan with conflict detection."""
        if start_date is None:
            start_date = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        if preferred_times is None:
            # Default preferred times: 6-9 AM and 6-9 PM
            preferred_times = [(6, 9), (18, 21)]
        
        scheduled_activities = []
        failed_activities = []
        
        # Track all scheduled slots to prevent double-booking (includes existing wellness events)
        occupied_slots = self._get_existing_wellness_events(start_date, start_date + timedelta(days=14))
        
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
                
                # Filter out slots that conflict with already scheduled activities
                available_slots = self._filter_conflicting_slots(free_slots, occupied_slots, duration)
                
                if available_slots:
                    # Choose best time based on activity type and user preferences
                    best_slot = self._choose_best_slot(activity, available_slots)
                    
                    if best_slot:
                        event_id = self.schedule_activity(activity, best_slot['start'])
                        
                        if event_id:
                            slot_end = best_slot['start'] + timedelta(minutes=duration)
                            
                            # Add this slot to occupied slots
                            occupied_slots.append({
                                'start': best_slot['start'],
                                'end': slot_end,
                                'activity_type': activity.get('type', 'unknown')
                            })
                            
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
                            'reason': 'No suitable time slot after conflict filtering',
                            'day': day_number
                        })
                else:
                    failed_activities.append({
                        'activity': activity,
                        'reason': 'No available time slots found (conflicts with other activities)',
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
        results_file = get_data_file_path('scheduling_results.json')
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def _filter_conflicting_slots(self, free_slots: List[Dict[str, Any]], 
                                 occupied_slots: List[Dict[str, Any]], duration_minutes: int) -> List[Dict[str, Any]]:
        """Filter out free slots that would conflict with already scheduled activities."""
        if not occupied_slots:
            return free_slots
        
        available_slots = []
        
        for slot in free_slots:
            slot_start = slot['start']
            slot_end = slot_start + timedelta(minutes=duration_minutes)
            
            # Check if this slot conflicts with any occupied slot
            conflicts = False
            for occupied in occupied_slots:
                # Check for overlap: slot conflicts if it starts before occupied ends and ends after occupied starts
                if (slot_start < occupied['end'] and slot_end > occupied['start']):
                    conflicts = True
                    break
            
            # Add buffer time between activities (minimum 15 minutes gap)
            if not conflicts:
                for occupied in occupied_slots:
                    time_gap_before = abs((slot_start - occupied['end']).total_seconds() / 60)
                    time_gap_after = abs((occupied['start'] - slot_end).total_seconds() / 60)
                    
                    # If the activities are on the same day and too close together
                    if (slot_start.date() == occupied['start'].date() and 
                        (time_gap_before < 15 and time_gap_before > -duration_minutes) or
                        (time_gap_after < 15 and time_gap_after > -duration_minutes)):
                        conflicts = True
                        break
            
            if not conflicts:
                available_slots.append(slot)
        
        return available_slots
    
    def _get_existing_wellness_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get existing wellness events to include in conflict detection."""
        existing_events = []
        
        if not self.service:
            return existing_events  # Return empty list in demo mode
        
        try:
            # Ensure datetime has timezone info for API call
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                q='Personal AI Wellness Assistant'  # Filter for our events
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Skip all-day events
                if 'T' not in start:
                    continue
                
                existing_events.append({
                    'start': datetime.fromisoformat(start.replace('Z', '+00:00')),
                    'end': datetime.fromisoformat(end.replace('Z', '+00:00')),
                    'activity_type': 'existing_wellness_event',
                    'event_id': event.get('id'),
                    'summary': event.get('summary', '')
                })
            
            print(f"🗓️  Found {len(existing_events)} existing wellness events to avoid conflicts")
            
        except Exception as e:
            print(f"⚠️  Could not fetch existing wellness events: {e}")
        
        return existing_events
    
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
    
    def detect_duplicate_events(self, start_date: datetime = None, end_date: datetime = None, 
                               time_tolerance_minutes: int = 5) -> List[Dict[str, Any]]:
        """Detect duplicate wellness events in the calendar."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now() + timedelta(days=30)
            
        if not self.service:
            return []  # Return empty list in demo mode
            
        try:
            # Get all wellness events in the date range
            events = self._get_existing_wellness_events(start_date, end_date)
            duplicates = []
            
            # Compare each event with every other event
            for i, event1 in enumerate(events):
                for j, event2 in enumerate(events):
                    if i >= j:  # Skip self-comparison and already checked pairs
                        continue
                    
                    # Check if events are duplicates based on multiple criteria
                    if self._are_events_duplicates(event1, event2, time_tolerance_minutes):
                        duplicate_pair = {
                            'event1': {
                                'id': event1.get('event_id'),
                                'summary': event1.get('summary', ''),
                                'start': event1['start'].isoformat(),
                                'end': event1['end'].isoformat(),
                                'description': event1.get('description', '')
                            },
                            'event2': {
                                'id': event2.get('event_id'),
                                'summary': event2.get('summary', ''),
                                'start': event2['start'].isoformat(),
                                'end': event2['end'].isoformat(),
                                'description': event2.get('description', '')
                            },
                            'similarity_score': self._calculate_similarity_score(event1, event2),
                            'detected_at': datetime.now().isoformat()
                        }
                        duplicates.append(duplicate_pair)
            
            return duplicates
            
        except Exception as e:
            print(f"Error detecting duplicate events: {e}")
            return []
    
    def _are_events_duplicates(self, event1: Dict[str, Any], event2: Dict[str, Any], 
                              time_tolerance_minutes: int = 5) -> bool:
        """Determine if two events are duplicates based on similarity criteria."""
        # Check time similarity (within tolerance)
        time_diff = abs((event1['start'] - event2['start']).total_seconds() / 60)
        if time_diff > time_tolerance_minutes:
            return False
        
        # Check duration similarity
        duration1 = (event1['end'] - event1['start']).total_seconds() / 60
        duration2 = (event2['end'] - event2['start']).total_seconds() / 60
        duration_diff = abs(duration1 - duration2)
        if duration_diff > time_tolerance_minutes:
            return False
        
        # Check title/summary similarity
        summary1 = event1.get('summary', '').lower().strip()
        summary2 = event2.get('summary', '').lower().strip()
        
        # Remove common prefixes/emojis for comparison
        summary1_clean = self._clean_event_title(summary1)
        summary2_clean = self._clean_event_title(summary2)
        
        if summary1_clean == summary2_clean:
            return True
        
        # Check if one title contains the other (partial match)
        if summary1_clean in summary2_clean or summary2_clean in summary1_clean:
            return True
        
        return False
    
    def _clean_event_title(self, title: str) -> str:
        """Clean event title for comparison by removing emojis and common prefixes."""
        import re
        
        # Remove emojis
        title = re.sub(r'[^\w\s-]', '', title)
        
        # Remove common wellness prefixes
        prefixes_to_remove = ['morning', 'evening', 'afternoon', 'daily', 'weekly']
        words = title.lower().split()
        filtered_words = [word for word in words if word not in prefixes_to_remove]
        
        return ' '.join(filtered_words).strip()
    
    def _calculate_similarity_score(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculate similarity score between two events (0-100)."""
        score = 0.0
        
        # Time similarity (40% weight)
        time_diff_minutes = abs((event1['start'] - event2['start']).total_seconds() / 60)
        time_score = max(0, 40 - (time_diff_minutes * 2))  # Decrease score by 2 per minute difference
        score += time_score
        
        # Duration similarity (20% weight)
        duration1 = (event1['end'] - event1['start']).total_seconds() / 60
        duration2 = (event2['end'] - event2['start']).total_seconds() / 60
        duration_diff = abs(duration1 - duration2)
        duration_score = max(0, 20 - duration_diff)
        score += duration_score
        
        # Title similarity (40% weight)
        summary1 = self._clean_event_title(event1.get('summary', ''))
        summary2 = self._clean_event_title(event2.get('summary', ''))
        
        if summary1 == summary2:
            title_score = 40
        elif summary1 in summary2 or summary2 in summary1:
            title_score = 30
        else:
            title_score = 0
        
        score += title_score
        
        return min(100.0, score)
    
    def get_duplicate_groups(self, start_date: datetime = None, end_date: datetime = None,
                            min_similarity_score: float = 80.0) -> List[Dict[str, Any]]:
        """Group duplicate events together for easier management."""
        duplicates = self.detect_duplicate_events(start_date, end_date)
        
        # Group duplicates by creating clusters of similar events
        processed_event_ids: Set[str] = set()
        duplicate_groups = []
        
        for duplicate_pair in duplicates:
            event1_id = duplicate_pair['event1']['id']
            event2_id = duplicate_pair['event2']['id']
            
            # Skip if either event already processed
            if event1_id in processed_event_ids or event2_id in processed_event_ids:
                continue
            
            # Only include high-similarity duplicates
            if duplicate_pair['similarity_score'] < min_similarity_score:
                continue
            
            # Create a new group
            group = {
                'group_id': f"dup_group_{len(duplicate_groups) + 1}",
                'events': [duplicate_pair['event1'], duplicate_pair['event2']],
                'similarity_score': duplicate_pair['similarity_score'],
                'recommended_action': self._get_recommended_action(duplicate_pair),
                'created_at': datetime.now().isoformat()
            }
            
            duplicate_groups.append(group)
            processed_event_ids.add(event1_id)
            processed_event_ids.add(event2_id)
        
        return duplicate_groups
    
    def _get_recommended_action(self, duplicate_pair: Dict[str, Any]) -> Dict[str, Any]:
        """Determine recommended action for handling a duplicate pair."""
        event1 = duplicate_pair['event1']
        event2 = duplicate_pair['event2']
        
        # Prefer event with more complete information
        event1_completeness = self._calculate_event_completeness(event1)
        event2_completeness = self._calculate_event_completeness(event2)
        
        if event1_completeness > event2_completeness:
            recommended_keep = event1['id']
            recommended_delete = event2['id']
            reason = "Event 1 has more complete information"
        elif event2_completeness > event1_completeness:
            recommended_keep = event2['id']
            recommended_delete = event1['id']
            reason = "Event 2 has more complete information"
        else:
            # If equal completeness, prefer the later created one (assuming more recent)
            # Since we can't get creation time easily, prefer event1 by default
            recommended_keep = event1['id']
            recommended_delete = event2['id']
            reason = "Events have equal information - keeping first occurrence"
        
        return {
            'action': 'delete_duplicate',
            'keep_event_id': recommended_keep,
            'delete_event_id': recommended_delete,
            'reason': reason,
            'confidence': 'high' if abs(event1_completeness - event2_completeness) > 20 else 'medium'
        }
    
    def _calculate_event_completeness(self, event: Dict[str, Any]) -> int:
        """Calculate completeness score for an event (0-100)."""
        score = 0
        
        # Has summary (20 points)
        if event.get('summary'):
            score += 20
        
        # Has description (30 points)
        description = event.get('description', '')
        if description:
            score += 30
            # Extra points for detailed descriptions
            if len(description) > 50:
                score += 10
        
        # Has proper time info (20 points)
        if event.get('start') and event.get('end'):
            score += 20
        
        # Has meaningful title (not just generic) (20 points)
        summary = event.get('summary', '').lower()
        if summary and 'activity' not in summary and 'exercise' not in summary:
            score += 20
        
        return min(100, score)
    
    def resolve_duplicates(self, duplicate_groups: List[Dict[str, Any]] = None, 
                          resolution_strategy: str = 'recommended', dry_run: bool = False) -> Dict[str, Any]:
        """Resolve duplicate events by deleting unwanted duplicates."""
        if duplicate_groups is None:
            duplicate_groups = self.get_duplicate_groups()
        
        resolution_result = {
            'timestamp': datetime.now().isoformat(),
            'total_groups': len(duplicate_groups),
            'processed_groups': 0,
            'deleted_events': [],
            'kept_events': [],
            'failed_deletions': [],
            'dry_run': dry_run
        }
        
        if not self.service and not dry_run:
            print("⚠️  No calendar service available - running in dry run mode")
            dry_run = True
            resolution_result['dry_run'] = True
        
        for group in duplicate_groups:
            try:
                # Determine which event to keep based on strategy
                keep_event_id, delete_event_id = self._determine_resolution_action(group, resolution_strategy)
                
                if dry_run:
                    print(f"🔍 [DRY RUN] Would delete event {delete_event_id}, keep {keep_event_id}")
                    resolution_result['deleted_events'].append({
                        'event_id': delete_event_id,
                        'status': 'would_delete',
                        'reason': group['recommended_action']['reason']
                    })
                    resolution_result['kept_events'].append(keep_event_id)
                else:
                    # Actually delete the duplicate event
                    success = self._delete_single_event(delete_event_id)
                    
                    if success:
                        print(f"✅ Deleted duplicate event {delete_event_id}")
                        resolution_result['deleted_events'].append({
                            'event_id': delete_event_id,
                            'status': 'deleted',
                            'reason': group['recommended_action']['reason']
                        })
                        resolution_result['kept_events'].append(keep_event_id)
                    else:
                        print(f"❌ Failed to delete event {delete_event_id}")
                        resolution_result['failed_deletions'].append({
                            'event_id': delete_event_id,
                            'reason': 'API deletion failed'
                        })
                
                resolution_result['processed_groups'] += 1
                
            except Exception as e:
                print(f"❌ Error processing duplicate group: {e}")
                resolution_result['failed_deletions'].append({
                    'group_id': group.get('group_id', 'unknown'),
                    'reason': str(e)
                })
        
        # Log the resolution results
        self._log_duplicate_resolution(resolution_result)
        
        return resolution_result
    
    def _determine_resolution_action(self, group: Dict[str, Any], strategy: str) -> Tuple[str, str]:
        """Determine which event to keep and which to delete based on strategy."""
        recommended = group['recommended_action']
        
        if strategy == 'recommended':
            return recommended['keep_event_id'], recommended['delete_event_id']
        elif strategy == 'keep_first':
            events = group['events']
            return events[0]['id'], events[1]['id']
        elif strategy == 'keep_last':
            events = group['events']
            return events[1]['id'], events[0]['id']
        else:
            # Default to recommended
            return recommended['keep_event_id'], recommended['delete_event_id']
    
    def _delete_single_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """Delete a single event by ID."""
        if not self.service:
            return False
        
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting event {event_id}: {e}")
            return False
    
    def _log_duplicate_resolution(self, resolution_result: Dict[str, Any]) -> None:
        """Log duplicate resolution results for audit trail."""
        try:
            log_file = get_data_file_path('duplicate_resolution_log.json')
            
            # Load existing log or create new
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'resolution_history': []}
            
            # Add new resolution
            log_data['resolution_history'].append(resolution_result)
            
            # Keep only last 50 resolutions to prevent file from growing too large
            if len(log_data['resolution_history']) > 50:
                log_data['resolution_history'] = log_data['resolution_history'][-50:]
            
            # Save updated log
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)
            
            print(f"📝 Resolution logged to {log_file}")
            
        except Exception as e:
            print(f"⚠️  Failed to log resolution: {e}")
    
    def delete_duplicate_events_batch(self, event_ids: List[str], dry_run: bool = False) -> Dict[str, Any]:
        """Delete multiple duplicate events in batch with safety checks."""
        result = {
            'timestamp': datetime.now().isoformat(),
            'requested_deletions': len(event_ids),
            'successful_deletions': 0,
            'failed_deletions': [],
            'deleted_event_ids': [],
            'dry_run': dry_run
        }
        
        if not self.service and not dry_run:
            dry_run = True
            result['dry_run'] = True
            print("⚠️  No calendar service - running in dry run mode")
        
        # Safety check: prevent deleting too many events at once
        if len(event_ids) > 20:
            print(f"⚠️  Safety limit: Cannot delete more than 20 events at once (requested: {len(event_ids)})")
            result['failed_deletions'].append({
                'reason': 'Safety limit exceeded (max 20 events)',
                'event_count': len(event_ids)
            })
            return result
        
        for event_id in event_ids:
            try:
                if dry_run:
                    print(f"🔍 [DRY RUN] Would delete event: {event_id}")
                    result['deleted_event_ids'].append(event_id)
                else:
                    success = self._delete_single_event(event_id)
                    if success:
                        result['successful_deletions'] += 1
                        result['deleted_event_ids'].append(event_id)
                        print(f"✅ Deleted event: {event_id}")
                    else:
                        result['failed_deletions'].append({
                            'event_id': event_id,
                            'reason': 'API deletion failed'
                        })
            
            except Exception as e:
                result['failed_deletions'].append({
                    'event_id': event_id,
                    'reason': str(e)
                })
        
        # Log batch deletion
        self._log_duplicate_resolution(result)
        
        return result
    
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
        
        # Ensure timezone info
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        
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