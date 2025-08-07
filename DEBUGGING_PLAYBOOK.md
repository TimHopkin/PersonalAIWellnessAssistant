# Debugging Playbook - Common Issues & Fast Solutions

This playbook provides step-by-step solutions for common development issues using the fast development workflow.

## 🎯 Chat Function Issues

### Issue: "Chat dialog closes when I hit enter"

#### **Fast Diagnosis (30 seconds):**
1. Open `http://localhost:8080/debug/chat-test`
2. Look at connection status indicators
3. Try sending a test message
4. Watch the API log panel (right side)

#### **Common Causes & Solutions:**

**Cause 1: JavaScript Event Handling**
- **Symptoms**: Dialog closes immediately, no API call in logs
- **Solution**: Check browser console (F12) for JavaScript errors
- **Fix**: Edit `static/js/main.js`, refresh browser (no rebuild needed)

**Cause 2: API Endpoint Failing**
- **Symptoms**: API call appears in logs but returns error
- **Solution**: Check development server console for red error messages
- **Fix**: Debug backend code, server auto-restarts on changes

**Cause 3: AI Integration Issue**
- **Symptoms**: API call succeeds but no AI response
- **Solution**: Check `http://localhost:8080/debug/ai-status`
- **Fix**: Verify API keys in environment variables

### Issue: "AI doesn't respond to messages"

#### **Fast Diagnosis (15 seconds):**
```bash
curl -X POST http://localhost:8080/debug/chat-direct \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, are you working?"}'
```

#### **Solutions by Response:**

**Response: 500 Error**
- **Cause**: AI service unavailable or API key issues
- **Check**: `http://localhost:8080/debug/ai-status`
- **Fix**: Update API keys in environment variables

**Response: Success but no content**
- **Cause**: AI response parsing issue
- **Check**: Development server logs for parsing errors
- **Fix**: Review `src/plan_generator.py` chat methods

**Response: Timeout**
- **Cause**: AI service slow or network issues
- **Check**: Internet connection, API service status
- **Fix**: Add timeout handling or retry logic

## 🔧 Development Server Issues

### Issue: "Address already in use - Port 8080"

#### **Fast Solution (10 seconds):**
```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Or use different port
python3 run_dev.py --port 8081
```

### Issue: "Import errors when starting server"

#### **Fast Diagnosis:**
```bash
# Check you're in correct directory
pwd
# Should end with: Personal AI Wellness Assistant

# Check Python path
python3 -c "import sys; print(sys.path)"
```

#### **Solutions:**
- Ensure you're in project root directory
- Check all required packages are installed
- Verify `src/` directory structure is intact

### Issue: "Changes not appearing"

#### **For Frontend Changes (HTML/CSS/JS):**
1. **Hard refresh**: Ctrl+Shift+R (Chrome/Firefox)
2. **Check caching**: Development server disables caching
3. **Verify file path**: Ensure editing correct file

#### **For Backend Changes (Python):**
1. **Check console**: Server should show "Restarting with stat"
2. **Verify syntax**: Check for Python syntax errors
3. **Watch logs**: Look for import or runtime errors

## 🐛 API Issues

### Issue: "API returns 500 errors"

#### **Fast Debugging Steps:**

1. **Check console logs** (immediate):
   - Look for red error messages
   - Check stack traces

2. **Check debug.log** (detailed):
   ```bash
   tail -f debug.log
   ```

3. **Test isolated endpoint**:
   ```bash
   curl -X GET http://localhost:8080/debug/ai-status
   ```

#### **Common API Fixes:**
- **Missing data**: Add validation logging
- **Database issues**: Check data directory permissions
- **Import errors**: Verify all modules are available

### Issue: "Authentication/Session issues"

#### **Fast Diagnosis:**
```bash
# Check session management
curl -X GET http://localhost:8080/api/chat-sessions
```

#### **Solutions:**
- **Clear browser data**: Chrome Dev Tools → Application → Storage → Clear
- **Reset sessions**: Delete session files in `data/` directory
- **Check session logic**: Review `src/chat_manager.py`

## 📊 Performance Issues

### Issue: "App is slow or unresponsive"

#### **Performance Debugging:**

1. **Check console logs** for PERFORMANCE entries
2. **Monitor resource usage**:
   ```bash
   # Check memory/CPU usage
   top -p $(pgrep -f "python.*run_dev.py")
   ```

3. **Profile slow endpoints**:
   - Development logging shows timing for all API calls
   - Look for operations taking > 1000ms

#### **Common Performance Fixes:**
- **Database queries**: Add indexing or caching
- **AI API calls**: Add timeout and retry logic
- **File operations**: Use async operations for large files

## 🔍 Frontend Issues

### Issue: "JavaScript errors in browser"

#### **Fast Debugging:**
1. **Open DevTools**: F12 → Console tab
2. **Look for red errors**: Click for stack traces
3. **Check Network tab**: Look for failed requests
4. **Edit and test**: Modify `static/js/main.js`, refresh browser

#### **Common JavaScript Fixes:**
- **Null elements**: Add existence checks before using DOM elements
- **Async issues**: Add proper promise handling
- **Event conflicts**: Check for duplicate event listeners

### Issue: "CSS styling not working"

#### **Fast Solutions:**
1. **Hard refresh**: Ctrl+Shift+R
2. **Check inspector**: Right-click → Inspect → Styles tab
3. **Verify CSS path**: Ensure correct file being loaded
4. **Test changes**: Edit `static/css/main.css`, refresh browser

## 🚨 Emergency Procedures

### When Development Server Won't Start

#### **Recovery Steps:**
1. **Kill all Python processes**:
   ```bash
   pkill -f python
   ```

2. **Clean restart**:
   ```bash
   cd "Personal AI Wellness Assistant"
   python3 run_dev.py
   ```

3. **If still failing, check logs**:
   ```bash
   python3 run_dev.py 2>&1 | tee startup.log
   ```

### When Everything Seems Broken

#### **Nuclear Option:**
```bash
# Fall back to traditional build (slower but reliable)
python3 build_app.py
```

#### **Reset Development Environment:**
```bash
# Clear all cached data
rm -rf __pycache__ src/__pycache__
rm -f debug.log

# Restart fresh
python3 run_dev.py
```

## 🎯 Systematic Debugging Process

### Step 1: Identify the Layer
- **Frontend Issue**: Browser console errors, UI not responding
- **API Issue**: Network errors, 400/500 responses
- **Backend Issue**: Python errors, logic problems
- **Integration Issue**: Services not communicating

### Step 2: Use Appropriate Tool
- **Frontend**: Browser DevTools
- **API**: Debug endpoints (`/debug/chat-test`, `/debug/ai-status`)
- **Backend**: Development server console logs
- **Integration**: `debug.log` file and structured logging

### Step 3: Isolate the Problem
- **Test smallest unit**: Single function, single API call
- **Remove complexity**: Test without full app context
- **Check dependencies**: Verify external services are working

### Step 4: Fix and Verify
- **Make minimal change**: Target specific issue
- **Test immediately**: Use fast feedback loop
- **Verify fix**: Test both isolated and integrated scenarios

## 📈 Performance Benchmarks

### Expected Response Times (Development Mode)
- **Server startup**: 2-3 seconds
- **Hot reload**: < 1 second
- **Debug endpoints**: < 500ms
- **Simple API calls**: < 200ms
- **AI responses**: 2-10 seconds (external service)

### When to Escalate to Full Build
- **Desktop app testing**: Need WebView behavior
- **Production testing**: Performance under load
- **Distribution**: Creating installable packages
- **Final verification**: Before release

---

## 💡 Pro Tips

1. **Always start with debug endpoints** - fastest way to isolate issues
2. **Use structured logging** - grep for specific error types
3. **Test incrementally** - make small changes, verify each one
4. **Keep browser DevTools open** - catch frontend issues immediately
5. **Watch console logs** - real-time feedback on backend issues

**Remember**: The goal is to debug in seconds/minutes, not hours. If you're spending too much time on one issue, step back and use the isolation tools to narrow down the problem.