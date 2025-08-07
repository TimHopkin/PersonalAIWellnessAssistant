# Personal AI Wellness Assistant

🌟 Your AI-powered companion for holistic wellness! This application combines personalized wellness planning with smart calendar scheduling, progress tracking, and **AI chat for plan modifications**.

## Features

- **🎯 AI-Powered Wellness Plans**: Generate personalized workout, meditation, and nutrition plans using Grok AI
- **💬 AI Chat Interface**: Modify your wellness plan through natural language conversations
- **📅 Smart Scheduling**: Automatically schedule activities on Google Calendar based on your availability
- **📊 Progress Tracking**: Track your daily progress with manual input and device integration stubs
- **🔄 Adaptive Planning**: Plans automatically adapt based on your completion rates and feedback
- **📈 Analytics**: Weekly reports and wellness trend analysis
- **🖥️ Desktop & Web Interface**: Beautiful web interface accessible as desktop app or in browser

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Credentials

#### Grok API (Required)
1. Get SuperGrok/Premium+ subscription at https://x.ai
2. Get API key from https://x.ai/api
3. Copy `.env.example` to `.env` and add your key:
   ```
   GROK_API_KEY=your_key_here
   ```

#### Google Calendar (Required)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials file as `credentials.json` in the project directory

#### Device Integration (Optional)
- **Garmin**: Sign up at [Garmin Developer Program](https://developer.garmin.com/gc-developer-program/)
- **Renpho**: Use your existing Renpho app credentials

### 3. Run the Application

**Desktop App (Recommended):**
```bash
python3 desktop_app.py
```

**Web Only:**
```bash
python3 app.py
```

## Usage Guide

### First Time Setup
1. Run `python3 desktop_app.py`
2. Navigate to the **Profile** page to create your profile
3. Go to the **Wellness Plan** page to generate your first AI-powered plan
4. Use the **Schedule** page to add activities to your Google Calendar
5. **Try the AI Chat**: On the Wellness Plan page, click "Chat with AI" to modify your plan using natural language!

### Daily Use
1. Use the **Progress** page to log your daily activities
2. Check the **Reports** page to see your progress and trends
3. **Chat with AI** to adjust your plan: "Make tomorrow's workout easier" or "Add more meditation time"
4. The system will suggest plan adaptations based on your progress

## File Structure

```
├── desktop_app.py          # Desktop application launcher
├── app.py                  # Flask web application
├── profile_manager.py      # User profile management
├── plan_generator.py       # AI wellness plan generation with chat updates
├── calendar_integration.py # Google Calendar integration
├── progress_tracker.py     # Progress tracking and device stubs
├── chat_manager.py         # AI chat session management
├── data_utils.py          # Data storage utilities
├── templates/             # HTML templates for web interface
├── static/               # CSS, JavaScript, and images
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file

# Generated files (created during use)
├── profile.json           # Your profile data
├── wellness_plan.json     # Current wellness plan
├── progress_data.json     # Progress tracking data
├── chat_history.json      # AI chat conversation history
├── backups/              # Plan version backups
├── scheduling_results.json # Calendar scheduling results
├── credentials.json       # Google OAuth credentials (you provide)
└── token.pickle          # Google OAuth token (auto-generated)
```

## API Costs & Limits

### Grok API
- **Model**: grok-beta (~$0.30-$0.50/million tokens)
- **Usage**: ~1000-5000 tokens per plan generation
- **Estimated Cost**: $0.001-$0.005 per plan

### Google Calendar API
- **Free tier**: 1 billion requests/month
- **Cost**: Free for personal use

### Device APIs
- **Garmin**: Free for approved developers
- **Renpho**: Unofficial API (no official costs)

## Configuration Options

### Environment Variables
Copy `.env.example` to `.env` and configure:

- `GROK_API_KEY`: Your Grok API key (required)
- `GARMIN_CLIENT_ID`: Garmin OAuth client ID (optional)
- `GARMIN_CLIENT_SECRET`: Garmin OAuth secret (optional)
- `RENPHO_EMAIL`: Renpho account email (optional)
- `RENPHO_PASSWORD`: Renpho account password (optional)

### Profile Customization
The profile supports:
- Demographics (age, weight, height)
- Fitness level (beginner/intermediate/advanced)
- Activity preferences (running, yoga, meditation, etc.)
- Time constraints and availability
- Personal goals and constraints

## Device Integration

### Current Status
- **Garmin**: Stub implementation with manual fallback
- **Renpho**: Stub implementation with manual fallback

### Future Enhancement
Both integrations are stubbed for the MVP but include the framework for:
- OAuth authentication flows
- API endpoint integration
- Automatic data syncing

## Troubleshooting

### Common Issues

**"GROK_API_KEY not found"**
- Ensure you've created `.env` file with your API key
- Check that your Grok subscription is active

**"Calendar authentication failed"**
- Verify `credentials.json` is in the project directory
- Ensure Google Calendar API is enabled in Google Cloud Console
- Delete `token.pickle` and re-authenticate if needed

**"No activities planned for today"**
- Generate a wellness plan first
- Ensure the plan start date includes today
- Check that activities were successfully scheduled

**"Error generating plan"**
- Check your internet connection
- Verify Grok API key is valid and has quota
- Try using the fallback plan generator

### Reset Everything
To start fresh, delete these files:
```bash
rm profile.json wellness_plan.json progress_data.json token.pickle scheduling_results.json
```

## Development Notes

### Code Structure
- **Modular design**: Each component (profile, planning, calendar, tracking) is separate
- **Error handling**: Graceful fallbacks for API failures
- **Data persistence**: JSON files for local storage
- **Extensible**: Easy to add new features and integrations

### Extending the MVP
1. **Web Interface**: Replace CLI with Flask/FastAPI web app
2. **Database**: Replace JSON files with PostgreSQL/SQLite
3. **Advanced AI**: Use Grok-2 for more sophisticated planning
4. **Real Device Integration**: Implement full OAuth flows
5. **Team Features**: Multi-user support and social features

## Security Notes

- Store API keys in `.env` file (never commit to version control)
- Google OAuth tokens are stored locally in `token.pickle`
- Profile data stays on your local machine
- Device credentials are optional and only for your personal use

## License

Personal use only. This MVP is designed for individual wellness management.

---

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all API credentials are correctly configured
3. Verify your internet connection and API quotas
4. Try running individual components to isolate issues

**Example Test Commands:**
```bash
# Test profile manager
python profile_manager.py

# Test plan generation
python plan_generator.py

# Test calendar integration
python calendar_integration.py

# Test progress tracking
python progress_tracker.py
```

---

**Happy wellness journey! 🌟💪**