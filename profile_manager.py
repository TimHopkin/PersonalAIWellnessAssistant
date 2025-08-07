import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from data_utils import get_data_file_path

class ProfileManager:
    def __init__(self, profile_file: str = "profile.json"):
        self.profile_file = get_data_file_path(profile_file)
        
    def get_profile(self) -> Dict[str, Any]:
        """Collect user profile information through command-line input."""
        print("\n=== Personal AI Wellness Assistant - Profile Setup ===")
        print("Please provide your information to create a personalized wellness plan.\n")
        
        profile = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Basic demographics
        while True:
            try:
                profile["age"] = int(input("Enter your age: "))
                if 13 <= profile["age"] <= 120:
                    break
                print("Please enter a valid age between 13 and 120.")
            except ValueError:
                print("Please enter a valid number for age.")
        
        while True:
            try:
                profile["weight"] = float(input("Enter your weight (kg): "))
                if 30 <= profile["weight"] <= 300:
                    break
                print("Please enter a valid weight between 30 and 300 kg.")
            except ValueError:
                print("Please enter a valid number for weight.")
        
        while True:
            try:
                profile["height"] = float(input("Enter your height (cm): "))
                if 100 <= profile["height"] <= 250:
                    break
                print("Please enter a valid height between 100 and 250 cm.")
            except ValueError:
                print("Please enter a valid number for height.")
        
        # Fitness level
        while True:
            fitness_level = input("Fitness level (beginner/intermediate/advanced): ").lower().strip()
            if fitness_level in ["beginner", "intermediate", "advanced"]:
                profile["fitness_level"] = fitness_level
                break
            print("Please enter 'beginner', 'intermediate', or 'advanced'.")
        
        # Goals
        profile["goals"] = input("What are your wellness goals? (e.g., lose 10kg, run 5K, reduce stress): ").strip()
        
        # Constraints and preferences
        profile["constraints"] = input("Any constraints or preferences? (e.g., no workouts before 7AM, vegetarian diet): ").strip()
        
        # Activity preferences
        print("\nActivity preferences (enter 'yes' or 'no'):")
        activities = ["running", "cycling", "yoga", "stretching", "meditation", "strength_training"]
        profile["activity_preferences"] = {}
        
        for activity in activities:
            while True:
                preference = input(f"Do you enjoy {activity}? (yes/no): ").lower().strip()
                if preference in ["yes", "no"]:
                    profile["activity_preferences"][activity] = preference == "yes"
                    break
                print("Please enter 'yes' or 'no'.")
        
        # Available time slots
        profile["available_time_slots"] = input("What times work best for activities? (e.g., 6-8 AM, 6-8 PM): ").strip()
        
        # Save profile
        self.save_profile(profile)
        print(f"\nProfile saved successfully to {self.profile_file}!")
        return profile
    
    def load_profile(self) -> Optional[Dict[str, Any]]:
        """Load existing profile from file."""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None
        return None
    
    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Save profile to file with backup and error handling."""
        try:
            # Update timestamp
            profile["updated_at"] = datetime.now().isoformat()
            
            # Create backup of existing profile if it exists
            if self.profile_file.exists():
                backup_file = self.profile_file.with_suffix('.json.backup')
                import shutil
                shutil.copy2(self.profile_file, backup_file)
                print(f"📄 Created profile backup: {backup_file}")
            
            # Write to temporary file first for atomic operation
            temp_file = self.profile_file.with_suffix('.json.tmp')
            with open(temp_file, 'w') as f:
                json.dump(profile, f, indent=2)
            
            # Verify the file was written correctly
            with open(temp_file, 'r') as f:
                test_load = json.load(f)
                if not test_load.get('age') or not test_load.get('weight'):
                    raise ValueError("Profile data appears corrupted")
            
            # Atomically replace the original file
            if temp_file.exists():
                temp_file.replace(self.profile_file)
                print(f"✅ Profile saved successfully to: {self.profile_file}")
            else:
                raise FileNotFoundError("Temporary file was not created properly")
            
        except Exception as e:
            print(f"❌ Error saving profile: {e}")
            # Try to restore backup if available
            backup_file = self.profile_file.with_suffix('.json.backup')
            if backup_file.exists():
                backup_file.replace(self.profile_file)
                print(f"🔄 Restored profile from backup")
            raise e
    
    def update_profile(self) -> Dict[str, Any]:
        """Update existing profile or create new one."""
        existing_profile = self.load_profile()
        
        if existing_profile:
            print(f"\nExisting profile found (created: {existing_profile.get('created_at', 'Unknown')}).")
            choice = input("Would you like to (u)pdate it or create a (n)ew profile? (u/n): ").lower().strip()
            
            if choice == 'u':
                print("\nCurrent profile summary:")
                print(f"Age: {existing_profile.get('age', 'Not set')}")
                print(f"Weight: {existing_profile.get('weight', 'Not set')} kg")
                print(f"Fitness Level: {existing_profile.get('fitness_level', 'Not set')}")
                print(f"Goals: {existing_profile.get('goals', 'Not set')}")
                
                update_choice = input("\nWhat would you like to update? (goals/constraints/all/none): ").lower().strip()
                
                if update_choice == "goals":
                    existing_profile["goals"] = input("Enter new goals: ").strip()
                elif update_choice == "constraints":
                    existing_profile["constraints"] = input("Enter new constraints: ").strip()
                elif update_choice == "all":
                    return self.get_profile()
                elif update_choice == "none":
                    return existing_profile
                
                self.save_profile(existing_profile)
                return existing_profile
        
        return self.get_profile()
    
    def display_profile(self, profile: Dict[str, Any]) -> None:
        """Display profile information in a formatted way."""
        print("\n=== Your Profile ===")
        print(f"Age: {profile.get('age')} years")
        print(f"Weight: {profile.get('weight')} kg")
        print(f"Height: {profile.get('height')} cm")
        print(f"Fitness Level: {profile.get('fitness_level', '').title()}")
        print(f"Goals: {profile.get('goals')}")
        print(f"Constraints: {profile.get('constraints')}")
        print(f"Available Times: {profile.get('available_time_slots')}")
        
        print("\nActivity Preferences:")
        for activity, likes in profile.get('activity_preferences', {}).items():
            status = "✓" if likes else "✗"
            print(f"  {status} {activity.replace('_', ' ').title()}")
        print()

if __name__ == "__main__":
    manager = ProfileManager()
    profile = manager.update_profile()
    manager.display_profile(profile)