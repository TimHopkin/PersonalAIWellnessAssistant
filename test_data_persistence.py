#!/usr/bin/env python3
"""
Comprehensive Data Persistence Testing Script
Tests profile saving, loading, and data integrity across different scenarios.
"""

import json
import os
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from profile_manager import ProfileManager
from plan_generator import PlanGenerator
from progress_tracker import ProgressTracker
from chat_manager import ChatManager
from data_utils import get_data_file_path, get_data_directory, get_app_info

class DataPersistenceTest:
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.original_cwd = None
    
    def setup_test_environment(self):
        """Set up isolated test environment."""
        print("🔧 Setting up test environment...")
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp(prefix="wellness_test_")
        os.chdir(self.temp_dir)
        print(f"📁 Test directory: {self.temp_dir}")
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"🗑️  Cleaned up test directory: {self.temp_dir}")
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message}")
    
    def create_test_profile(self) -> Dict[str, Any]:
        """Create a test profile with known data."""
        return {
            "created_at": "2025-08-07T10:00:00",
            "updated_at": "2025-08-07T10:00:00",
            "age": 35,
            "weight": 70.5,
            "height": 175.0,
            "fitness_level": "intermediate",
            "goals": "improve cardiovascular health and lose 5kg",
            "constraints": "prefer morning workouts, no equipment",
            "available_time_slots": "6-8 AM, 7-9 PM",
            "activity_preferences": {
                "running": True,
                "cycling": False,
                "yoga": True,
                "stretching": True,
                "meditation": True,
                "strength_training": False
            }
        }
    
    def test_data_directory_setup(self):
        """Test data directory creation and permissions."""
        try:
            info = get_app_info()
            data_dir = Path(info['data_directory'])
            
            # Test directory exists
            exists = data_dir.exists()
            self.log_test("Data Directory Exists", exists, f"Path: {data_dir}")
            
            # Test write permissions
            writable = info['is_writable']
            self.log_test("Data Directory Writable", writable, "Can write to data directory")
            
            # Test file path generation
            test_file_path = get_data_file_path("test.json")
            path_correct = str(test_file_path).endswith("test.json")
            self.log_test("File Path Generation", path_correct, f"Generated: {test_file_path}")
            
        except Exception as e:
            self.log_test("Data Directory Setup", False, f"Error: {e}")
    
    def test_profile_basic_operations(self):
        """Test basic profile save/load operations."""
        try:
            manager = ProfileManager()
            test_profile = self.create_test_profile()
            
            # Test save
            manager.save_profile(test_profile)
            save_success = manager.profile_file.exists()
            self.log_test("Profile Save", save_success, f"File created: {manager.profile_file}")
            
            # Test load
            loaded_profile = manager.load_profile()
            load_success = loaded_profile is not None
            self.log_test("Profile Load", load_success, f"Profile loaded: {loaded_profile is not None}")
            
            # Test data integrity
            if loaded_profile:
                age_match = loaded_profile.get('age') == test_profile['age']
                weight_match = loaded_profile.get('weight') == test_profile['weight']
                goals_match = loaded_profile.get('goals') == test_profile['goals']
                
                integrity_success = age_match and weight_match and goals_match
                self.log_test("Profile Data Integrity", integrity_success, 
                            f"Age: {age_match}, Weight: {weight_match}, Goals: {goals_match}")
                
                # Test creation time preservation
                created_preserved = loaded_profile.get('created_at') == test_profile['created_at']
                self.log_test("Creation Time Preserved", created_preserved,
                            f"Original: {test_profile['created_at']}, Loaded: {loaded_profile.get('created_at')}")
            
        except Exception as e:
            self.log_test("Profile Basic Operations", False, f"Error: {e}")
    
    def test_profile_update_scenarios(self):
        """Test profile update scenarios that might cause data loss."""
        try:
            manager = ProfileManager()
            original_profile = self.create_test_profile()
            
            # Save original profile
            manager.save_profile(original_profile)
            
            # Simulate web form update (the problematic scenario)
            updated_profile = {
                "age": 36,  # Changed
                "weight": 68.0,  # Changed
                "height": 175.0,
                "fitness_level": "advanced",  # Changed
                "goals": "train for marathon",  # Changed
                "constraints": "prefer morning workouts, no equipment",
                "available_time_slots": "5-7 AM",  # Changed
                "activity_preferences": {
                    "running": True,
                    "cycling": True,  # Changed
                    "yoga": True,
                    "stretching": True,
                    "meditation": False,  # Changed
                    "strength_training": True  # Changed
                },
                "updated_at": datetime.now().isoformat()
            }
            
            # Load existing profile and preserve created_at (simulating fixed logic)
            existing = manager.load_profile()
            if existing and existing.get('created_at'):
                updated_profile['created_at'] = existing['created_at']
            else:
                updated_profile['created_at'] = datetime.now().isoformat()
            
            # Save updated profile
            manager.save_profile(updated_profile)
            
            # Verify the update preserved original creation time
            final_profile = manager.load_profile()
            creation_preserved = final_profile.get('created_at') == original_profile['created_at']
            data_updated = final_profile.get('age') == 36 and final_profile.get('fitness_level') == 'advanced'
            
            self.log_test("Profile Update - Creation Time Preserved", creation_preserved,
                         f"Original: {original_profile['created_at']}, Final: {final_profile.get('created_at')}")
            self.log_test("Profile Update - Data Changed", data_updated,
                         f"Age: {final_profile.get('age')}, Fitness: {final_profile.get('fitness_level')}")
            
        except Exception as e:
            self.log_test("Profile Update Scenarios", False, f"Error: {e}")
    
    def test_profile_backup_and_recovery(self):
        """Test profile backup and recovery mechanisms."""
        try:
            manager = ProfileManager()
            test_profile = self.create_test_profile()
            
            # Save initial profile
            manager.save_profile(test_profile)
            
            # Check backup was created
            backup_file = manager.profile_file.with_suffix('.json.backup')
            backup_created = backup_file.exists()
            self.log_test("Profile Backup Created", backup_created, f"Backup: {backup_file}")
            
            # Simulate corruption scenario
            if backup_created:
                # Corrupt the main profile file
                with open(manager.profile_file, 'w') as f:
                    f.write("invalid json content")
                
                # Try to load - should fail
                corrupted_profile = manager.load_profile()
                corruption_detected = corrupted_profile is None
                self.log_test("Corruption Detection", corruption_detected, "Detected invalid profile")
                
                # Restore from backup manually (simulating recovery)
                if backup_file.exists():
                    shutil.copy2(backup_file, manager.profile_file)
                    recovered_profile = manager.load_profile()
                    recovery_success = recovered_profile is not None and recovered_profile.get('age') == test_profile['age']
                    self.log_test("Profile Recovery", recovery_success, "Recovered from backup successfully")
            
        except Exception as e:
            self.log_test("Profile Backup and Recovery", False, f"Error: {e}")
    
    def test_concurrent_access(self):
        """Test handling of concurrent profile access."""
        try:
            import threading
            import time
            
            manager = ProfileManager()
            test_profile = self.create_test_profile()
            
            errors = []
            success_count = 0
            
            def save_profile_thread(thread_id):
                nonlocal success_count, errors
                try:
                    modified_profile = test_profile.copy()
                    modified_profile['age'] = 30 + thread_id
                    modified_profile['goals'] = f"Goals from thread {thread_id}"
                    manager.save_profile(modified_profile)
                    success_count += 1
                except Exception as e:
                    errors.append(f"Thread {thread_id}: {e}")
            
            # Start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=save_profile_thread, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check final profile is valid
            final_profile = manager.load_profile()
            final_valid = final_profile is not None and 30 <= final_profile.get('age', 0) <= 34
            
            self.log_test("Concurrent Access", len(errors) == 0 and final_valid,
                         f"Successes: {success_count}, Errors: {len(errors)}, Final age: {final_profile.get('age') if final_profile else 'None'}")
            
        except Exception as e:
            self.log_test("Concurrent Access", False, f"Error: {e}")
    
    def test_data_validation(self):
        """Test data validation prevents corruption."""
        try:
            manager = ProfileManager()
            
            # Test invalid data scenarios
            invalid_profiles = [
                {"age": "invalid", "weight": 70, "height": 175},  # Invalid age type
                {"age": 150, "weight": 70, "height": 175},        # Age out of range
                {"age": 30, "weight": "invalid", "height": 175},   # Invalid weight type
                {"age": 30, "weight": 5, "height": 175},          # Weight out of range
                {"age": 30, "weight": 70, "height": "invalid"},   # Invalid height type
                {"age": 30, "weight": 70, "height": 50},          # Height out of range
            ]
            
            validation_errors = 0
            for i, invalid_profile in enumerate(invalid_profiles):
                try:
                    # This should fail validation in the web app
                    invalid_profile.update({
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "fitness_level": "beginner",
                        "goals": "test",
                        "constraints": "",
                        "available_time_slots": "",
                        "activity_preferences": {}
                    })
                    manager.save_profile(invalid_profile)
                    # If we get here, validation failed
                    validation_errors += 1
                except (ValueError, TypeError):
                    # Expected - validation caught the error
                    pass
            
            self.log_test("Data Validation", validation_errors == 0,
                         f"Validation errors: {validation_errors}/6 scenarios")
            
        except Exception as e:
            self.log_test("Data Validation", False, f"Error: {e}")
    
    def test_other_data_components(self):
        """Test other data persistence components."""
        try:
            # Test plan persistence
            plan_generator = PlanGenerator()
            test_plan = {
                "plan_name": "Test Plan",
                "generated_at": datetime.now().isoformat(),
                "days": [{"day": 1, "activities": []}]
            }
            
            plan_generator.save_plan(test_plan)
            loaded_plan = plan_generator.load_plan()
            plan_success = loaded_plan is not None and loaded_plan.get('plan_name') == 'Test Plan'
            self.log_test("Plan Persistence", plan_success, f"Plan saved and loaded correctly")
            
            # Test progress persistence
            progress_tracker = ProgressTracker()
            test_progress = {
                "created_at": datetime.now().isoformat(),
                "daily_logs": {
                    "2025-08-07": {
                        "date": "2025-08-07",
                        "completed_activities": [],
                        "energy_level": 8
                    }
                }
            }
            
            progress_tracker.save_progress(test_progress)
            loaded_progress = progress_tracker.load_progress()
            progress_success = loaded_progress is not None and len(loaded_progress.get('daily_logs', {})) > 0
            self.log_test("Progress Persistence", progress_success, f"Progress saved and loaded correctly")
            
            # Test chat history persistence
            chat_manager = ChatManager()
            session_id = chat_manager.start_new_session()
            chat_manager.add_user_message("Test message", session_id)
            chat_manager.add_ai_response("Test response", [], session_id)
            
            context = chat_manager.get_conversation_context(session_id)
            chat_success = len(context) >= 2  # User message + AI response
            self.log_test("Chat Persistence", chat_success, f"Chat history: {len(context)} messages")
            
        except Exception as e:
            self.log_test("Other Data Components", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all data persistence tests."""
        print("=" * 60)
        print("🧪 PERSONAL AI WELLNESS ASSISTANT - DATA PERSISTENCE TESTS")
        print("=" * 60)
        
        try:
            self.setup_test_environment()
            
            # Run test suites
            self.test_data_directory_setup()
            self.test_profile_basic_operations()
            self.test_profile_update_scenarios()
            self.test_profile_backup_and_recovery()
            self.test_concurrent_access()
            self.test_data_validation()
            self.test_other_data_components()
            
        finally:
            self.cleanup_test_environment()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print(f"\n{'🎉 ALL TESTS PASSED!' if failed_tests == 0 else '⚠️  Some tests failed - check the issues above'}")
        
        # Save detailed results
        results_file = Path("test_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0,
                    'run_at': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")

def main():
    """Main entry point for testing script."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("🚀 Running quick profile test...")
        # Quick test just for profile issues
        tester = DataPersistenceTest()
        try:
            tester.setup_test_environment()
            tester.test_profile_basic_operations()
            tester.test_profile_update_scenarios()
        finally:
            tester.cleanup_test_environment()
        tester.print_test_summary()
    else:
        # Run full test suite
        tester = DataPersistenceTest()
        tester.run_all_tests()

if __name__ == "__main__":
    main()