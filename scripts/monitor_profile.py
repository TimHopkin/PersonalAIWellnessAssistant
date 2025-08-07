#!/usr/bin/env python3
"""
Profile Monitoring Script
Real-time monitoring of profile changes to catch data loss issues.
"""

import json
import time
import hashlib
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to the path to import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from profile_manager import ProfileManager

class ProfileMonitor:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.profile_file = self.profile_manager.profile_file
        self.last_hash = None
        self.last_content = None
        self.change_history = []
    
    def get_file_hash(self, file_path):
        """Get MD5 hash of file content."""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return None
    
    def load_profile_safely(self):
        """Load profile with error handling."""
        try:
            return self.profile_manager.load_profile()
        except Exception as e:
            return {"error": str(e)}
    
    def check_profile_changes(self):
        """Check for profile changes and log them."""
        current_hash = self.get_file_hash(self.profile_file)
        
        if current_hash != self.last_hash:
            timestamp = datetime.now().isoformat()
            current_content = self.load_profile_safely()
            
            change_info = {
                "timestamp": timestamp,
                "file_exists": self.profile_file.exists(),
                "hash": current_hash,
                "previous_hash": self.last_hash,
                "profile_data": current_content
            }
            
            if self.last_content:
                # Check what changed
                changes = self.detect_changes(self.last_content, current_content)
                change_info["changes"] = changes
            
            self.change_history.append(change_info)
            self.print_change(change_info)
            
            self.last_hash = current_hash
            self.last_content = current_content
    
    def detect_changes(self, old_profile, new_profile):
        """Detect specific changes between profile versions."""
        if isinstance(old_profile, dict) and isinstance(new_profile, dict):
            changes = []
            
            # Check each field
            fields_to_check = ['age', 'weight', 'height', 'fitness_level', 'goals', 'constraints', 'created_at', 'updated_at']
            
            for field in fields_to_check:
                old_val = old_profile.get(field)
                new_val = new_profile.get(field)
                
                if old_val != new_val:
                    changes.append({
                        "field": field,
                        "old_value": old_val,
                        "new_value": new_val
                    })
            
            # Check activity preferences
            old_prefs = old_profile.get('activity_preferences', {})
            new_prefs = new_profile.get('activity_preferences', {})
            
            for activity in set(list(old_prefs.keys()) + list(new_prefs.keys())):
                old_pref = old_prefs.get(activity)
                new_pref = new_prefs.get(activity)
                
                if old_pref != new_pref:
                    changes.append({
                        "field": f"activity_preferences.{activity}",
                        "old_value": old_pref,
                        "new_value": new_pref
                    })
            
            return changes
        else:
            return [{"field": "entire_profile", "old_value": str(old_profile), "new_value": str(new_profile)}]
    
    def print_change(self, change_info):
        """Print formatted change information."""
        print(f"\n🔄 Profile Change Detected at {change_info['timestamp']}")
        print(f"📁 File exists: {change_info['file_exists']}")
        print(f"🔒 Hash: {change_info['hash'][:8]}...")
        
        if "error" in change_info.get("profile_data", {}):
            print(f"❌ Error loading profile: {change_info['profile_data']['error']}")
        elif isinstance(change_info.get("profile_data"), dict):
            profile = change_info["profile_data"]
            print(f"👤 Age: {profile.get('age')}, Weight: {profile.get('weight')}, Fitness: {profile.get('fitness_level')}")
            print(f"🎯 Goals: {profile.get('goals', '')[:50]}...")
            print(f"📅 Created: {profile.get('created_at', 'Unknown')[:19]}")
            print(f"📝 Updated: {profile.get('updated_at', 'Unknown')[:19]}")
        
        if change_info.get("changes"):
            print(f"🔍 Changes detected:")
            for change in change_info["changes"][:5]:  # Show first 5 changes
                print(f"  • {change['field']}: {change['old_value']} → {change['new_value']}")
            
            if len(change_info["changes"]) > 5:
                print(f"  ... and {len(change_info['changes']) - 5} more changes")
        
        print("-" * 60)
    
    def save_history(self):
        """Save change history to file."""
        history_file = Path("profile_change_history.json")
        with open(history_file, 'w') as f:
            json.dump({
                "monitoring_started": datetime.now().isoformat(),
                "total_changes": len(self.change_history),
                "changes": self.change_history
            }, f, indent=2)
        
        print(f"📄 Change history saved to: {history_file}")
    
    def start_monitoring(self, check_interval=2):
        """Start monitoring profile changes."""
        print("=" * 60)
        print("👁️  PROFILE MONITOR STARTED")
        print("=" * 60)
        print(f"📁 Monitoring: {self.profile_file}")
        print(f"⏱️  Check interval: {check_interval} seconds")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Initial check
        self.check_profile_changes()
        
        try:
            while True:
                time.sleep(check_interval)
                self.check_profile_changes()
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Monitoring stopped")
            print(f"📊 Total changes detected: {len(self.change_history)}")
            
            if self.change_history:
                self.save_history()
            
            return self.change_history

def main():
    """Main entry point."""
    import sys
    
    monitor = ProfileMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        # Just show current profile status
        print("📋 Current Profile Status:")
        print("-" * 40)
        
        profile = monitor.load_profile_safely()
        if isinstance(profile, dict) and "error" not in profile:
            print(f"✅ Profile loaded successfully")
            print(f"👤 Age: {profile.get('age')}, Weight: {profile.get('weight')}, Height: {profile.get('height')}")
            print(f"💪 Fitness Level: {profile.get('fitness_level', 'Not set')}")
            print(f"🎯 Goals: {profile.get('goals', 'Not set')}")
            print(f"📅 Created: {profile.get('created_at', 'Unknown')}")
            print(f"📝 Updated: {profile.get('updated_at', 'Unknown')}")
            
            # Show activity preferences
            prefs = profile.get('activity_preferences', {})
            if prefs:
                print(f"🏃 Activities: {', '.join([k for k, v in prefs.items() if v])}")
        
        elif isinstance(profile, dict) and "error" in profile:
            print(f"❌ Error loading profile: {profile['error']}")
        else:
            print("❌ No profile found")
        
        print(f"📁 Profile file: {monitor.profile_file}")
        print(f"📂 File exists: {monitor.profile_file.exists()}")
    else:
        # Start monitoring
        monitor.start_monitoring()

if __name__ == "__main__":
    main()