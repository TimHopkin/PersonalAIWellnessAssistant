#!/usr/bin/env python3
"""
Simple test of PyWebView functionality
"""

import webview
import threading
import time

def test_webview():
    """Test basic webview functionality"""
    print("Testing PyWebView...")
    
    # Create a simple window
    try:
        window = webview.create_window(
            title='Test Window',
            url='https://www.google.com',
            width=800,
            height=600
        )
        
        print("Window created successfully")
        
        # Start webview with a timeout
        def close_after_delay():
            time.sleep(3)  # Wait 3 seconds
            webview.destroy_window(window)
        
        # Start close timer
        timer_thread = threading.Thread(target=close_after_delay, daemon=True)
        timer_thread.start()
        
        webview.start(debug=False)
        print("WebView test completed successfully")
        return True
        
    except Exception as e:
        print(f"WebView test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_webview()
    if success:
        print("✅ PyWebView is working correctly")
    else:
        print("❌ PyWebView has issues")