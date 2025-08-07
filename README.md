# Personal AI Wellness Assistant

A desktop application that combines AI-powered wellness planning with intelligent calendar integration.

## Project Structure

```
Personal AI Wellness Assistant/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                  # This file
│
├── src/                       # Core application code
│   ├── __init__.py
│   ├── app.py                # Flask web server
│   ├── desktop_app.py        # PyWebView desktop wrapper
│   ├── profile_manager.py    # User profile management
│   ├── plan_generator.py     # AI wellness plan generation
│   ├── calendar_integration.py # Google Calendar integration
│   ├── progress_tracker.py   # Progress and activity tracking
│   ├── chat_manager.py       # AI chat conversation management
│   └── data_utils.py         # Data directory and file utilities
│
├── templates/                 # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── plan.html
│   ├── progress.html
│   ├── schedule.html
│   ├── settings.html
│   └── reports.html
│
├── static/                    # Web assets
│   ├── css/
│   │   └── main.css
│   ├── js/
│   │   └── main.js
│   └── img/
│
├── tests/                     # Test scripts
│   ├── test_data_persistence.py
│   ├── test_calendar_integration.py
│   ├── test_results.json
│   └── calendar_test_results.json
│
├── scripts/                   # Utility and monitoring scripts
│   ├── monitor_profile.py
│   ├── monitor_calendar.py
│   ├── create_icon.py
│   └── scheduling_results.json
│
├── data/                      # Application data files
│   ├── profile.json
│   ├── wellness_plan.json
│   ├── progress_data.json
│   ├── chat_history.json
│   ├── calendar_integration_report.json
│   └── server.log
│
├── config/                    # Configuration files
│   ├── requirements.txt       # Original requirements
│   └── token.pickle          # Google API tokens
│
├── assets/                    # Application assets
│   ├── wellness_icon.svg
│   ├── wellness_icon.icns
│   └── favicon.ico
│
├── backups/                   # Automated backups
│   └── wellness_plan_backup_*.json
│
└── docs/                      # Documentation
    ├── PROJECT_OVERVIEW.md
    ├── README.md (original)
    └── netlify-conversion-plan.txt
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   - Copy your Google Calendar credentials to `config/`
   - Set up your Grok API key in `.env` file

3. **Run Application**
   ```bash
   python main.py
   ```

## Testing

- **Data Persistence**: `python tests/test_data_persistence.py`
- **Calendar Integration**: `python tests/test_calendar_integration.py`

## Monitoring

- **Profile Monitoring**: `python scripts/monitor_profile.py`
- **Calendar Health**: `python scripts/monitor_calendar.py`

## Key Features

- ✅ AI-powered wellness plan generation
- ✅ Google Calendar integration with conflict detection  
- ✅ Progress tracking and analytics
- ✅ Interactive AI chat interface
- ✅ Atomic data persistence with backups
- ✅ Real-time monitoring capabilities
- ✅ Comprehensive testing framework

See `docs/PROJECT_OVERVIEW.md` for detailed information about the application architecture, functionality, and development roadmap.