#!/usr/bin/env python3
"""
Personal AI Wellness Assistant - Web Application
Flask web interface for the wellness assistant.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Environment variables are loaded by desktop_app.py

# Import existing components
from profile_manager import ProfileManager
from plan_generator import PlanGenerator
from calendar_integration import CalendarIntegration
from progress_tracker import ProgressTracker
from chat_manager import ChatManager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'wellness-assistant-secret-key')
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

# Add template filters for date formatting
@app.template_filter('format_date')
def format_date(value):
    """Format date for display"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime('%A, %B %d, %Y')
    return str(value)

@app.template_filter('format_time')
def format_time(value):
    """Format time for display"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime('%I:%M %p')
    return str(value)

@app.template_filter('format_date_input')
def format_date_input(value):
    """Format date for HTML date input"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return str(value)

# Add context processors to make common functions available in templates
@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    def get_today():
        return datetime.now()
    
    def get_tomorrow():
        return datetime.now() + timedelta(days=1)
    
    def format_current_date():
        return datetime.now().strftime('%A, %B %d, %Y')
    
    return dict(
        get_today=get_today,
        get_tomorrow=get_tomorrow,
        format_current_date=format_current_date
    )

# Initialize components
profile_manager = ProfileManager()
plan_generator = PlanGenerator()
calendar_integration = CalendarIntegration()
progress_tracker = ProgressTracker()
chat_manager = ChatManager()

# Initialize calendar authentication on startup
print("🗓️  Initializing Google Calendar integration...")
calendar_integration.authenticate()

@app.route('/')
def dashboard():
    """Main dashboard page."""
    # Get current data
    profile = profile_manager.load_profile()
    plan = plan_generator.load_plan()
    progress_data = progress_tracker.load_progress()
    
    # Calculate dashboard stats
    dashboard_stats = calculate_dashboard_stats(profile, plan, progress_data)
    
    return render_template('dashboard.html', 
                         stats=dashboard_stats,
                         profile=profile,
                         plan=plan)

@app.route('/profile')
def profile_page():
    """Profile management page."""
    profile = profile_manager.load_profile()
    return render_template('profile.html', profile=profile)

@app.route('/profile', methods=['POST'])
def save_profile():
    """Save profile data."""
    try:
        # Load existing profile to preserve creation time and other data
        existing_profile = profile_manager.load_profile()
        
        # Create new profile data
        profile_data = {
            'age': int(request.form.get('age', 0)),
            'weight': float(request.form.get('weight', 0)),
            'height': float(request.form.get('height', 0)),
            'fitness_level': request.form.get('fitness_level', 'beginner'),
            'goals': request.form.get('goals', ''),
            'constraints': request.form.get('constraints', ''),
            'available_time_slots': request.form.get('available_time_slots', ''),
            'activity_preferences': {
                'running': 'running' in request.form.getlist('activities'),
                'cycling': 'cycling' in request.form.getlist('activities'),
                'yoga': 'yoga' in request.form.getlist('activities'),
                'stretching': 'stretching' in request.form.getlist('activities'),
                'meditation': 'meditation' in request.form.getlist('activities'),
                'strength_training': 'strength_training' in request.form.getlist('activities')
            },
            'updated_at': datetime.now().isoformat()
        }
        
        # Preserve existing creation time or create new one
        if existing_profile and existing_profile.get('created_at'):
            profile_data['created_at'] = existing_profile['created_at']
        else:
            profile_data['created_at'] = datetime.now().isoformat()
        
        # Validate the data
        if profile_data['age'] < 13 or profile_data['age'] > 120:
            flash('Please enter a valid age between 13 and 120', 'error')
            return redirect(url_for('profile_page'))
        
        if profile_data['weight'] < 30 or profile_data['weight'] > 300:
            flash('Please enter a valid weight between 30 and 300 kg', 'error')
            return redirect(url_for('profile_page'))
        
        if profile_data['height'] < 100 or profile_data['height'] > 250:
            flash('Please enter a valid height between 100 and 250 cm', 'error')
            return redirect(url_for('profile_page'))
        
        # Save the profile
        profile_manager.save_profile(profile_data)
        flash('Profile saved successfully!', 'success')
        
        # Log successful save for debugging
        print(f"✅ Profile saved successfully at {datetime.now().isoformat()}")
        print(f"📁 Profile file location: {profile_manager.profile_file}")
        
    except ValueError as e:
        flash(f'Invalid input: Please check your entries and try again', 'error')
        print(f"❌ Profile validation error: {e}")
    except Exception as e:
        flash(f'Error saving profile: {str(e)}', 'error')
        print(f"❌ Profile save error: {e}")
    
    return redirect(url_for('profile_page'))

@app.route('/plan')
def plan_page():
    """Plan generation page."""
    profile = profile_manager.load_profile()
    plan = plan_generator.load_plan()
    
    return render_template('plan.html', profile=profile, plan=plan)

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    """Generate a new wellness plan."""
    try:
        profile = profile_manager.load_profile()
        if not profile:
            return jsonify({'error': 'Please create a profile first'}), 400
        
        days = int(request.form.get('days', 7))
        plan = plan_generator.generate_plan(profile, days)
        
        return jsonify({
            'success': True,
            'message': 'Plan generated successfully!',
            'plan': plan
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/schedule')
def schedule_page():
    """Calendar scheduling page."""
    plan = plan_generator.load_plan()
    
    # Get upcoming activities
    try:
        upcoming_activities = calendar_integration.get_upcoming_activities(7)
    except Exception as e:
        upcoming_activities = []
    
    return render_template('schedule.html', 
                         plan=plan, 
                         upcoming_activities=upcoming_activities)

@app.route('/schedule-plan', methods=['POST'])
def schedule_plan():
    """Schedule the wellness plan on calendar with conflict detection."""
    try:
        plan = plan_generator.load_plan()
        if not plan:
            return jsonify({'error': 'No plan found to schedule'}), 400
        
        start_date_str = request.form.get('start_date')
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() + timedelta(days=1)
        
        # Get preferred times from form
        preferred_times = [(6, 9), (18, 21)]  # Default
        morning_slot = request.form.get('morning_slot')
        evening_slot = request.form.get('evening_slot')
        
        if morning_slot:
            try:
                start_h, end_h = map(int, morning_slot.split('-'))
                preferred_times[0] = (start_h, end_h)
            except ValueError:
                pass
        
        if evening_slot:
            try:
                start_h, end_h = map(int, evening_slot.split('-'))
                preferred_times[1] = (start_h, end_h)
            except ValueError:
                pass
        
        # Ensure calendar is authenticated
        print("🗓️  Authenticating with Google Calendar...")
        if not calendar_integration.authenticate():
            return jsonify({'error': 'Failed to authenticate with Google Calendar'}), 500
        
        # Schedule the plan with conflict detection
        print(f"📅 Scheduling {len(plan.get('days', []))} days of activities with conflict detection...")
        result = calendar_integration.schedule_wellness_plan(plan, start_date, preferred_times)
        
        # Provide detailed feedback about conflicts
        message = f'Scheduled {result["scheduled_count"]} activities'
        if result["failed_count"] > 0:
            message += f', {result["failed_count"]} failed due to conflicts'
        
        return jsonify({
            'success': True,
            'message': message,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress')
def progress_page():
    """Progress tracking page."""
    progress_data = progress_tracker.load_progress()
    plan = plan_generator.load_plan()
    
    # Calculate weekly stats
    weekly_stats = progress_tracker.calculate_weekly_progress(progress_data)
    
    return render_template('progress.html', 
                         progress_data=progress_data,
                         weekly_stats=weekly_stats,
                         plan=plan)

@app.route('/track-activity', methods=['POST'])
def track_activity():
    """Track completion of an activity."""
    try:
        activity_data = request.get_json()
        
        # Get current progress
        progress_data = progress_tracker.load_progress()
        today = str(datetime.now().date())
        
        # Initialize today's log if it doesn't exist
        if 'daily_logs' not in progress_data:
            progress_data['daily_logs'] = {}
        
        if today not in progress_data['daily_logs']:
            progress_data['daily_logs'][today] = {
                'date': today,
                'completed_activities': [],
                'skipped_activities': [],
                'notes': '',
                'energy_level': None,
                'mood_score': None
            }
        
        today_log = progress_data['daily_logs'][today]
        
        # Add the activity based on status
        if activity_data.get('status') == 'completed':
            today_log['completed_activities'].append({
                'activity': activity_data.get('activity', {}),
                'completion_time': datetime.now().isoformat(),
                'notes': activity_data.get('notes', ''),
                'full_completion': activity_data.get('full_completion', True),
                'partial_duration': activity_data.get('partial_duration', 0)
            })
        elif activity_data.get('status') == 'skipped':
            today_log['skipped_activities'].append({
                'activity': activity_data.get('activity', {}),
                'skip_reason': activity_data.get('notes', ''),
                'skip_time': datetime.now().isoformat()
            })
        
        # Update wellness scores if provided
        if activity_data.get('energy_level'):
            today_log['energy_level'] = int(activity_data['energy_level'])
        if activity_data.get('mood_score'):
            today_log['mood_score'] = int(activity_data['mood_score'])
        
        # Save progress
        progress_tracker.save_progress(progress_data)
        
        return jsonify({
            'success': True,
            'message': 'Activity tracked successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def reports_page():
    """Analytics and reports page."""
    progress_data = progress_tracker.load_progress()
    
    # Calculate various statistics
    weekly_stats = progress_tracker.calculate_weekly_progress(progress_data)
    
    # Prepare chart data
    chart_data = prepare_chart_data(progress_data)
    
    return render_template('reports.html', 
                         weekly_stats=weekly_stats,
                         chart_data=chart_data)

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """API endpoint for dashboard statistics."""
    profile = profile_manager.load_profile()
    plan = plan_generator.load_plan()
    progress_data = progress_tracker.load_progress()
    
    stats = calculate_dashboard_stats(profile, plan, progress_data)
    return jsonify(stats)

@app.route('/api/progress-chart-data')
def api_progress_chart_data():
    """API endpoint for progress chart data."""
    progress_data = progress_tracker.load_progress()
    chart_data = prepare_chart_data(progress_data)
    return jsonify(chart_data)

@app.route('/api/chat-update-plan', methods=['POST'])
def api_chat_update_plan():
    """API endpoint for chatting with AI to update wellness plan."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Start or resume chat session
        if not session_id:
            session_id = chat_manager.start_new_session()
        
        # Add user message to chat history
        chat_manager.add_user_message(message, session_id)
        
        # Load current plan
        plan = plan_generator.load_plan()
        if not plan:
            error_response = 'No wellness plan found. Please generate a plan first.'
            chat_manager.add_ai_response(error_response, [], session_id)
            return jsonify({
                'success': False, 
                'error': error_response,
                'session_id': session_id
            }), 400
        
        # Load user profile for context
        profile = profile_manager.load_profile()
        
        # Get conversation context
        conversation_context = chat_manager.get_conversation_context(session_id)
        
        # Process the chat message and get AI response
        try:
            response_data = plan_generator.process_chat_update(message, plan, profile, conversation_context)
            
            # Add AI response to chat history
            chat_manager.add_ai_response(
                response_data.get('response', 'Plan updated successfully!'),
                response_data.get('proposed_changes', []),
                session_id
            )
            
            return jsonify({
                'success': True,
                'response': response_data.get('response', 'Plan updated successfully!'),
                'proposed_changes': response_data.get('proposed_changes'),
                'plan_modified': response_data.get('plan_modified', False),
                'session_id': session_id
            })
        except Exception as e:
            error_response = 'Sorry, I encountered an error processing your request. Please try again.'
            chat_manager.add_ai_response(error_response, [], session_id)
            print(f"Error processing chat update: {e}")
            return jsonify({
                'success': False,
                'error': error_response,
                'session_id': session_id
            }), 500
        
    except Exception as e:
        print(f"Error in chat update API: {e}")
        return jsonify({'success': False, 'error': 'Invalid request'}), 500

@app.route('/api/chat-sessions')
def api_chat_sessions():
    """API endpoint to get active chat sessions."""
    try:
        # Clean up old sessions first
        cleaned_count = chat_manager.cleanup_old_sessions()
        if cleaned_count > 0:
            print(f"Cleaned up {cleaned_count} expired chat sessions")
        
        active_sessions = chat_manager.list_active_sessions()
        return jsonify({
            'success': True,
            'sessions': active_sessions,
            'total_sessions': len(active_sessions)
        })
    except Exception as e:
        print(f"Error getting chat sessions: {e}")
        return jsonify({'success': False, 'error': 'Failed to retrieve chat sessions'}), 500

@app.route('/api/plan-backups')
def api_plan_backups():
    """API endpoint to get available plan backups."""
    try:
        backups = plan_generator.list_plan_backups()
        return jsonify({
            'success': True,
            'backups': backups,
            'total_backups': len(backups)
        })
    except Exception as e:
        print(f"Error getting plan backups: {e}")
        return jsonify({'success': False, 'error': 'Failed to retrieve plan backups'}), 500

@app.route('/api/restore-plan-backup', methods=['POST'])
def api_restore_plan_backup():
    """API endpoint to restore a plan from backup."""
    try:
        data = request.get_json()
        backup_filename = data.get('backup_filename', '').strip()
        
        if not backup_filename:
            return jsonify({'success': False, 'error': 'Backup filename is required'}), 400
        
        success = plan_generator.restore_plan_backup(backup_filename)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Plan restored from backup: {backup_filename}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to restore plan from backup'
            }), 500
            
    except Exception as e:
        print(f"Error restoring plan backup: {e}")
        return jsonify({'success': False, 'error': 'Failed to restore plan backup'}), 500

def calculate_dashboard_stats(profile, plan, progress_data):
    """Calculate statistics for the dashboard."""
    stats = {
        'has_profile': profile is not None,
        'has_plan': plan is not None,
        'total_activities_today': 0,
        'completed_activities_today': 0,
        'current_streak': 0,
        'weekly_completion_rate': 0,
        'avg_energy_level': 0,
        'avg_mood_score': 0,
        'upcoming_activities': []
    }
    
    if progress_data and 'daily_logs' in progress_data:
        today = str(datetime.now().date())
        daily_logs = progress_data['daily_logs']
        
        # Today's activities
        if today in daily_logs:
            today_log = daily_logs[today]
            stats['completed_activities_today'] = len(today_log.get('completed_activities', []))
            stats['total_activities_today'] = (
                len(today_log.get('completed_activities', [])) + 
                len(today_log.get('skipped_activities', []))
            )
        
        # Weekly stats
        weekly_stats = progress_tracker.calculate_weekly_progress(progress_data)
        weekly_data = weekly_stats.get('stats', {})
        stats['weekly_completion_rate'] = weekly_data.get('activity_completion_rate', 0)
        stats['avg_energy_level'] = weekly_data.get('average_energy_level', 0)
        stats['avg_mood_score'] = weekly_data.get('average_mood_score', 0)
        
        # Calculate streak
        stats['current_streak'] = calculate_current_streak(daily_logs)
    
    # Upcoming activities
    try:
        stats['upcoming_activities'] = calendar_integration.get_upcoming_activities(3)
    except:
        stats['upcoming_activities'] = []
    
    return stats

def calculate_current_streak(daily_logs):
    """Calculate current consecutive days with completed activities."""
    if not daily_logs:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    while True:
        date_str = str(current_date)
        if date_str in daily_logs:
            day_log = daily_logs[date_str]
            if len(day_log.get('completed_activities', [])) > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        else:
            break
    
    return streak

def prepare_chart_data(progress_data):
    """Prepare data for charts and visualizations."""
    chart_data = {
        'completion_trend': [],
        'energy_trend': [],
        'mood_trend': [],
        'activity_distribution': {}
    }
    
    if not progress_data or 'daily_logs' not in progress_data:
        return chart_data
    
    daily_logs = progress_data['daily_logs']
    
    # Get last 7 days of data
    end_date = datetime.now().date()
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    for date_str in dates:
        if date_str in daily_logs:
            day_log = daily_logs[date_str]
            
            # Completion rate
            completed = len(day_log.get('completed_activities', []))
            total = completed + len(day_log.get('skipped_activities', []))
            completion_rate = completed / total if total > 0 else 0
            
            chart_data['completion_trend'].append({
                'date': date_str,
                'completion_rate': completion_rate * 100
            })
            
            # Energy and mood
            if day_log.get('energy_level'):
                chart_data['energy_trend'].append({
                    'date': date_str,
                    'energy': day_log['energy_level']
                })
            
            if day_log.get('mood_score'):
                chart_data['mood_trend'].append({
                    'date': date_str,
                    'mood': day_log['mood_score']
                })
            
            # Activity distribution
            for activity in day_log.get('completed_activities', []):
                activity_type = activity.get('activity', {}).get('type', 'unknown')
                chart_data['activity_distribution'][activity_type] = (
                    chart_data['activity_distribution'].get(activity_type, 0) + 1
                )
    
    return chart_data

@app.route('/settings')
def settings_page():
    """Settings page."""
    from data_utils import get_data_file_path
    
    # Check Google Calendar authentication status properly
    def check_calendar_auth():
        # Check if credentials file exists
        if not get_data_file_path('credentials.json').exists():
            return False
        
        # Check if we have a valid authentication token
        token_file = get_data_file_path('token.pickle')
        if not token_file.exists():
            return False
            
        # Try to verify the calendar service actually works
        try:
            from calendar_integration import CalendarIntegration
            test_calendar = CalendarIntegration()
            if test_calendar.authenticate() and test_calendar.service:
                # Test a simple API call
                test_calendar.service.calendarList().list(maxResults=1).execute()
                return True
        except Exception as e:
            print(f"Calendar auth test failed: {e}")
            return False
        
        return False
    
    # Check API status
    api_status = {
        'grok_api': bool(os.getenv('GROK_API_KEY')) and os.getenv('GROK_API_KEY') != 'your_grok_api_key_here',
        'google_calendar': check_calendar_auth(),
        'garmin': bool(os.getenv('GARMIN_CLIENT_ID')) and os.getenv('GARMIN_CLIENT_ID') != 'your_garmin_client_id_here',
        'renpho': bool(os.getenv('RENPHO_EMAIL')) and os.getenv('RENPHO_EMAIL') != 'your_renpho_email@example.com'
    }
    
    return render_template('settings.html', api_status=api_status)

@app.route('/debug-calendar')
def debug_calendar():
    """Debug calendar authentication status."""
    from data_utils import get_data_file_path
    import os
    
    debug_info = {
        'credentials_file': str(get_data_file_path('credentials.json')),
        'credentials_exists': get_data_file_path('credentials.json').exists(),
        'token_file': str(get_data_file_path('token.pickle')),
        'token_exists': get_data_file_path('token.pickle').exists(),
        'data_directory': str(get_data_file_path('').parent),
        'data_dir_writable': os.access(get_data_file_path('').parent, os.W_OK),
        'calendar_service_status': 'None'
    }
    
    # Test calendar authentication
    try:
        calendar_integration.authenticate()
        if calendar_integration.service:
            debug_info['calendar_service_status'] = 'Active'
            # Try a test API call
            try:
                cal_list = calendar_integration.service.calendarList().list(maxResults=1).execute()
                debug_info['api_test'] = 'Success'
                debug_info['calendar_count'] = len(cal_list.get('items', []))
            except Exception as e:
                debug_info['api_test'] = f'Failed: {e}'
        else:
            debug_info['calendar_service_status'] = 'Demo Mode'
    except Exception as e:
        debug_info['calendar_service_status'] = f'Error: {e}'
    
    return jsonify(debug_info)

@app.route('/reset-calendar-auth', methods=['POST'])
def reset_calendar_auth():
    """Reset calendar authentication to force re-auth."""
    try:
        success = calendar_integration.clear_authentication()
        if success:
            return jsonify({'success': True, 'message': 'Authentication cleared. Try scheduling again to re-authenticate.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to clear authentication'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/api/calendar-conflicts', methods=['POST'])
def api_calendar_conflicts():
    """Check for calendar conflicts before scheduling."""
    try:
        data = request.get_json()
        start_date_str = data.get('start_date')
        if not start_date_str:
            return jsonify({'error': 'start_date is required'}), 400
        
        start_date = datetime.fromisoformat(start_date_str)
        plan = plan_generator.load_plan()
        
        if not plan:
            return jsonify({'error': 'No wellness plan found'}), 400
        
        # Check for conflicts without actually scheduling
        calendar_integration.authenticate()
        end_date = start_date + timedelta(days=14)
        existing_events = calendar_integration._get_existing_wellness_events(start_date, end_date)
        busy_times = calendar_integration.get_busy_times(start_date, end_date)
        
        return jsonify({
            'success': True,
            'existing_wellness_events': len(existing_events),
            'busy_time_slots': len(busy_times),
            'conflicts_detected': len(existing_events) > 0,
            'preview_message': f'Found {len(existing_events)} existing wellness events and {len(busy_times)} busy time slots'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-wellness-events', methods=['POST'])
def api_delete_wellness_events():
    """Delete existing wellness events from calendar."""
    try:
        data = request.get_json()
        days_back = data.get('days_back', 7)
        days_forward = data.get('days_forward', 14)
        
        if not calendar_integration.authenticate():
            return jsonify({'error': 'Calendar authentication failed'}), 500
        
        # Get existing wellness events
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now() + timedelta(days=days_forward)
        existing_events = calendar_integration._get_existing_wellness_events(start_date, end_date)
        
        deleted_count = 0
        failed_count = 0
        
        for event in existing_events:
            try:
                calendar_integration.service.events().delete(
                    calendarId='primary', 
                    eventId=event['event_id']
                ).execute()
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete event {event['event_id']}: {e}")
                failed_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} wellness events, {failed_count} failed',
            'deleted_count': deleted_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    # Install Flask dependencies if not available
    try:
        import flask
        from flask_cors import CORS
    except ImportError:
        print("Installing Flask dependencies...")
        import subprocess
        subprocess.run(["pip3", "install", "flask", "flask-cors"])
        import flask
        from flask_cors import CORS
    
    print("🌟 Starting Personal AI Wellness Assistant Web Interface...")
    print("📱 Access the application at: http://localhost:8080")
    print("🚪 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=8080)