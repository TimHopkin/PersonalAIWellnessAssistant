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

# Import existing components
from profile_manager import ProfileManager
from plan_generator import PlanGenerator
from calendar_integration import CalendarIntegration
from progress_tracker import ProgressTracker

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'wellness-assistant-secret-key')
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
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        profile_manager.save_profile(profile_data)
        flash('Profile saved successfully!', 'success')
        
    except Exception as e:
        flash(f'Error saving profile: {str(e)}', 'error')
    
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
    """Schedule the wellness plan on calendar."""
    try:
        plan = plan_generator.load_plan()
        if not plan:
            return jsonify({'error': 'No plan found to schedule'}), 400
        
        start_date_str = request.form.get('start_date')
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() + timedelta(days=1)
        
        # Schedule the plan
        result = calendar_integration.schedule_wellness_plan(plan, start_date)
        
        return jsonify({
            'success': True,
            'message': f'Scheduled {result["scheduled_count"]} activities',
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
    # Check API status
    api_status = {
        'grok_api': bool(os.getenv('GROK_API_KEY')),
        'google_calendar': os.path.exists('credentials.json'),
        'garmin': bool(os.getenv('GARMIN_CLIENT_ID')),
        'renpho': bool(os.getenv('RENPHO_EMAIL'))
    }
    
    return render_template('settings.html', api_status=api_status)

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