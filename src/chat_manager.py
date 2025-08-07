"""
Chat Manager for Personal AI Wellness Assistant
Manages conversation context and chat history.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
try:
    from .data_utils import get_data_file_path
except ImportError:
    from data_utils import get_data_file_path


class ChatManager:
    def __init__(self, chat_history_file: str = "chat_history.json"):
        self.chat_history_file = get_data_file_path(chat_history_file)
        self.current_session_id = None
        self.max_context_messages = 10  # Keep last 10 messages for context
        self.session_timeout_hours = 24  # Sessions expire after 24 hours
    
    def start_new_session(self) -> str:
        """Start a new chat session and return session ID."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id
        
        # Initialize session
        self._save_message(session_id, {
            'type': 'system',
            'timestamp': datetime.now().isoformat(),
            'message': 'Chat session started',
            'session_info': {
                'started_at': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat()
            }
        })
        
        return session_id
    
    def add_user_message(self, message: str, session_id: str = None) -> None:
        """Add a user message to the chat history."""
        if not session_id:
            session_id = self.current_session_id or self.start_new_session()
        
        self._save_message(session_id, {
            'type': 'user',
            'timestamp': datetime.now().isoformat(),
            'message': message
        })
        
        self._update_session_activity(session_id)
    
    def add_ai_response(self, response: str, changes_made: List[str] = None, session_id: str = None) -> None:
        """Add an AI response to the chat history."""
        if not session_id:
            session_id = self.current_session_id or self.start_new_session()
        
        message_data = {
            'type': 'ai',
            'timestamp': datetime.now().isoformat(),
            'message': response
        }
        
        if changes_made:
            message_data['changes_made'] = changes_made
        
        self._save_message(session_id, message_data)
        self._update_session_activity(session_id)
    
    def get_conversation_context(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Get recent conversation history for context."""
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id:
            return []
        
        history = self._load_chat_history()
        session_messages = history.get(session_id, {}).get('messages', [])
        
        # Filter out system messages and get recent messages
        conversation_messages = [
            msg for msg in session_messages 
            if msg.get('type') in ['user', 'ai']
        ]
        
        # Return last N messages for context
        return conversation_messages[-self.max_context_messages:]
    
    def get_session_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get a summary of the chat session."""
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id:
            return {}
        
        history = self._load_chat_history()
        session_data = history.get(session_id, {})
        
        if not session_data:
            return {}
        
        messages = session_data.get('messages', [])
        user_messages = [msg for msg in messages if msg.get('type') == 'user']
        ai_messages = [msg for msg in messages if msg.get('type') == 'ai']
        
        total_changes = 0
        for ai_msg in ai_messages:
            if ai_msg.get('changes_made'):
                total_changes += len(ai_msg['changes_made'])
        
        session_info = None
        for msg in messages:
            if msg.get('type') == 'system' and msg.get('session_info'):
                session_info = msg['session_info']
                break
        
        return {
            'session_id': session_id,
            'started_at': session_info.get('started_at') if session_info else None,
            'last_active': session_info.get('last_active') if session_info else None,
            'message_count': len(user_messages),
            'total_plan_changes': total_changes,
            'is_active': self._is_session_active(session_id)
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active chat sessions."""
        history = self._load_chat_history()
        active_sessions = []
        
        for session_id in history.keys():
            if self._is_session_active(session_id):
                summary = self.get_session_summary(session_id)
                if summary:
                    active_sessions.append(summary)
        
        # Sort by last active time
        active_sessions.sort(
            key=lambda x: x.get('last_active', ''), 
            reverse=True
        )
        
        return active_sessions
    
    def cleanup_old_sessions(self) -> int:
        """Clean up expired chat sessions and return count of removed sessions."""
        history = self._load_chat_history()
        expired_sessions = []
        
        for session_id in list(history.keys()):
            if not self._is_session_active(session_id):
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            del history[session_id]
        
        if expired_sessions:
            self._save_chat_history(history)
        
        return len(expired_sessions)
    
    def _save_message(self, session_id: str, message_data: Dict[str, Any]) -> None:
        """Save a message to the chat history."""
        history = self._load_chat_history()
        
        if session_id not in history:
            history[session_id] = {'messages': []}
        
        history[session_id]['messages'].append(message_data)
        
        # Limit message history per session
        max_messages_per_session = 100
        if len(history[session_id]['messages']) > max_messages_per_session:
            # Keep system messages and recent messages
            messages = history[session_id]['messages']
            system_messages = [msg for msg in messages if msg.get('type') == 'system']
            recent_messages = [msg for msg in messages if msg.get('type') != 'system'][-50:]
            history[session_id]['messages'] = system_messages + recent_messages
        
        self._save_chat_history(history)
    
    def _update_session_activity(self, session_id: str) -> None:
        """Update the last activity time for a session."""
        history = self._load_chat_history()
        
        if session_id in history:
            messages = history[session_id]['messages']
            for msg in messages:
                if msg.get('type') == 'system' and msg.get('session_info'):
                    msg['session_info']['last_active'] = datetime.now().isoformat()
                    break
            
            self._save_chat_history(history)
    
    def _is_session_active(self, session_id: str) -> bool:
        """Check if a session is still active (not expired)."""
        history = self._load_chat_history()
        session_data = history.get(session_id, {})
        
        if not session_data:
            return False
        
        messages = session_data.get('messages', [])
        last_active = None
        
        for msg in messages:
            if msg.get('type') == 'system' and msg.get('session_info'):
                last_active = msg['session_info'].get('last_active')
                break
        
        if not last_active:
            return False
        
        try:
            last_active_dt = datetime.fromisoformat(last_active)
            cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
            return last_active_dt > cutoff_time
        except:
            return False
    
    def _load_chat_history(self) -> Dict[str, Any]:
        """Load chat history from file."""
        if self.chat_history_file.exists():
            try:
                with open(self.chat_history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_chat_history(self, history: Dict[str, Any]) -> None:
        """Save chat history to file."""
        try:
            with open(self.chat_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")


if __name__ == "__main__":
    # Test the ChatManager
    chat_manager = ChatManager()
    
    session_id = chat_manager.start_new_session()
    print(f"Started session: {session_id}")
    
    chat_manager.add_user_message("Make my workouts easier", session_id)
    chat_manager.add_ai_response("I've reduced the intensity of your workouts.", ["Reduced running intensity to moderate"], session_id)
    
    context = chat_manager.get_conversation_context(session_id)
    print(f"Conversation context: {len(context)} messages")
    
    summary = chat_manager.get_session_summary(session_id)
    print(f"Session summary: {summary}")