import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
try:
    from .data_utils import get_data_file_path
except ImportError:
    from data_utils import get_data_file_path

load_dotenv()

class PlanGenerator:
    def __init__(self, plan_file: str = "wellness_plan.json"):
        self.plan_file = get_data_file_path(plan_file)
        self.client = None
        
        # Only initialize OpenAI client if API key is available
        api_key = os.getenv('GROK_API_KEY')
        if api_key and api_key != 'demo_key':
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url='https://api.x.ai/v1'
                )
            except Exception as e:
                print(f"Warning: Could not initialize Grok API: {e}")
                self.client = None
    
    def generate_plan(self, profile: Dict[str, Any], days: int = 7) -> Dict[str, Any]:
        """Generate a wellness plan using Grok API based on user profile."""
        if not self.client:
            print("⚠️  Grok API not configured - using fallback plan generation...")
            return self._generate_fallback_plan(profile, days)
        
        prompt = self._build_prompt(profile, days)
        
        try:
            print("🤖 Generating your personalized wellness plan with Grok AI...")
            response = self.client.chat.completions.create(
                model="grok-beta",  # Using grok-beta as it's available
                messages=[{
                    "role": "system",
                    "content": "You are a professional wellness coach and nutritionist. Generate comprehensive, safe, and personalized wellness plans in JSON format."
                }, {
                    "role": "user", 
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=4000
            )
            
            plan_content = response.choices[0].message.content
            
            # Clean up the response to extract JSON
            if "```json" in plan_content:
                plan_content = plan_content.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_content:
                plan_content = plan_content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(plan_content)
            
            # Add metadata
            plan["generated_at"] = datetime.now().isoformat()
            plan["profile_snapshot"] = profile
            plan["plan_duration"] = days
            
            # Validate plan structure
            self._validate_plan(plan)
            
            # Save plan
            self.save_plan(plan)
            print(f"Plan generated successfully and saved to {self.plan_file}!")
            
            return plan
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {e}")
            return self._generate_fallback_plan(profile, days)
        except Exception as e:
            print(f"Error generating plan: {e}")
            return self._generate_fallback_plan(profile, days)
    
    def _build_prompt(self, profile: Dict[str, Any], days: int) -> str:
        """Build the prompt for the AI based on user profile."""
        activity_prefs = profile.get('activity_preferences', {})
        liked_activities = [k for k, v in activity_prefs.items() if v]
        disliked_activities = [k for k, v in activity_prefs.items() if not v]
        
        prompt = f"""
Create a {days}-day personalized wellness plan for a {profile.get('age')}-year-old person.

PROFILE:
- Age: {profile.get('age')} years
- Weight: {profile.get('weight')} kg  
- Height: {profile.get('height')} cm
- Fitness Level: {profile.get('fitness_level')}
- Goals: {profile.get('goals')}
- Constraints: {profile.get('constraints')}
- Available Times: {profile.get('available_time_slots')}
- Likes: {', '.join(liked_activities) if liked_activities else 'None specified'}
- Dislikes: {', '.join(disliked_activities) if disliked_activities else 'None specified'}

REQUIREMENTS:
1. Include diverse activities: workouts (running, cycling, yoga, stretching, strength training), wellbeing (meditation, breathing exercises), and nutrition guidance
2. Respect their preferences and constraints
3. Ensure progressive difficulty appropriate for their fitness level
4. Provide specific durations, intensities, and instructions
5. Include rest days and recovery
6. Add nutritional recommendations for each day

Return ONLY valid JSON in this exact format:
{{
    "plan_name": "7-Day Personalized Wellness Plan",
    "days": [
        {{
            "day": 1,
            "date_offset": 0,
            "activities": [
                {{
                    "type": "running",
                    "category": "cardio",
                    "duration_minutes": 30,
                    "intensity": "moderate",
                    "details": "30-minute easy-paced run. Warm up 5 min, main run 20 min, cool down 5 min.",
                    "equipment_needed": "running shoes",
                    "best_time": "morning"
                }},
                {{
                    "type": "meditation",
                    "category": "wellbeing", 
                    "duration_minutes": 10,
                    "intensity": "low",
                    "details": "10-minute mindfulness meditation focusing on breath awareness.",
                    "equipment_needed": "none",
                    "best_time": "evening"
                }}
            ],
            "nutrition": {{
                "focus": "balanced macronutrients",
                "recommendations": [
                    "Start day with protein-rich breakfast",
                    "Include leafy greens in lunch",
                    "Stay hydrated - aim for 8 glasses of water"
                ]
            }},
            "notes": "Focus on establishing routine today"
        }}
    ],
    "weekly_goals": ["Build sustainable habits", "Improve cardiovascular health", "Enhance mindfulness"],
    "tips": ["Listen to your body", "Progress gradually", "Stay consistent"]
}}
"""
        return prompt
    
    def _validate_plan(self, plan: Dict[str, Any]) -> None:
        """Validate the generated plan has required structure."""
        required_keys = ["days", "plan_name"]
        for key in required_keys:
            if key not in plan:
                raise ValueError(f"Missing required key: {key}")
        
        if not isinstance(plan["days"], list) or len(plan["days"]) == 0:
            raise ValueError("Plan must have at least one day")
        
        for day in plan["days"]:
            if "activities" not in day or not isinstance(day["activities"], list):
                raise ValueError("Each day must have activities")
    
    def _generate_fallback_plan(self, profile: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Generate a basic fallback plan if AI fails."""
        print("Generating fallback plan...")
        
        fitness_level = profile.get('fitness_level', 'beginner')
        activity_prefs = profile.get('activity_preferences', {})
        
        # Adjust durations based on fitness level
        duration_map = {
            'beginner': {'cardio': 20, 'strength': 15, 'yoga': 15, 'meditation': 5},
            'intermediate': {'cardio': 30, 'strength': 25, 'yoga': 25, 'meditation': 10},
            'advanced': {'cardio': 45, 'strength': 35, 'yoga': 35, 'meditation': 15}
        }
        
        durations = duration_map.get(fitness_level, duration_map['beginner'])
        
        plan = {
            "plan_name": f"{days}-Day Wellness Plan (Fallback)",
            "generated_at": datetime.now().isoformat(),
            "profile_snapshot": profile,
            "plan_duration": days,
            "days": []
        }
        
        activity_rotation = [
            {"type": "walking", "category": "cardio", "intensity": "low"},
            {"type": "stretching", "category": "flexibility", "intensity": "low"},
            {"type": "bodyweight_exercises", "category": "strength", "intensity": "moderate"},
            {"type": "yoga", "category": "flexibility", "intensity": "low"},
            {"type": "rest", "category": "recovery", "intensity": "none"}
        ]
        
        for day_num in range(1, days + 1):
            activities = []
            
            # Add main activity (skip on rest days)
            if day_num % 5 != 0:  # Rest every 5th day
                main_activity = activity_rotation[(day_num - 1) % len(activity_rotation)]
                if main_activity["type"] != "rest":
                    duration = durations.get(main_activity["category"], 20)
                    activities.append({
                        "type": main_activity["type"],
                        "category": main_activity["category"],
                        "duration_minutes": duration,
                        "intensity": main_activity["intensity"],
                        "details": f"{duration}-minute {main_activity['type'].replace('_', ' ')} session",
                        "equipment_needed": "none",
                        "best_time": "flexible"
                    })
            
            # Add meditation
            activities.append({
                "type": "breathing_exercise",
                "category": "wellbeing",
                "duration_minutes": durations["meditation"],
                "intensity": "low",
                "details": f"{durations['meditation']}-minute deep breathing exercise",
                "equipment_needed": "none",
                "best_time": "evening"
            })
            
            plan["days"].append({
                "day": day_num,
                "date_offset": day_num - 1,
                "activities": activities,
                "nutrition": {
                    "focus": "balanced nutrition",
                    "recommendations": [
                        "Eat plenty of vegetables",
                        "Stay hydrated",
                        "Include lean proteins"
                    ]
                },
                "notes": "Rest day" if day_num % 5 == 0 else "Stay active"
            })
        
        plan["weekly_goals"] = ["Build healthy habits", "Increase daily movement", "Improve wellbeing"]
        plan["tips"] = ["Start slowly", "Listen to your body", "Be consistent"]
        
        self.save_plan(plan)
        return plan
    
    def load_plan(self) -> Optional[Dict[str, Any]]:
        """Load existing plan from file."""
        if self.plan_file.exists():
            try:
                with open(self.plan_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None
        return None
    
    def save_plan(self, plan: Dict[str, Any]) -> None:
        """Save plan to file and create backup version."""
        # Create backup of current plan if it exists
        self._create_plan_backup()
        
        with open(self.plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
    
    def _create_plan_backup(self) -> None:
        """Create a backup of the current plan."""
        if not self.plan_file.exists():
            return
        
        try:
            # Create backup directory
            backup_dir = self.plan_file.parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Load current plan to get timestamp
            current_plan = self.load_plan()
            if not current_plan:
                return
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'wellness_plan_backup_{timestamp}.json'
            backup_path = backup_dir / backup_filename
            
            # Copy current plan to backup
            import shutil
            shutil.copy2(self.plan_file, backup_path)
            
            # Limit number of backups (keep last 10)
            self._cleanup_old_backups(backup_dir, max_backups=10)
            
        except Exception as e:
            print(f"Warning: Could not create plan backup: {e}")
    
    def _cleanup_old_backups(self, backup_dir, max_backups: int = 10) -> None:
        """Remove old backup files, keeping only the most recent ones."""
        try:
            backup_files = list(backup_dir.glob('wellness_plan_backup_*.json'))
            if len(backup_files) <= max_backups:
                return
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                print(f"Removed old backup: {backup_file.name}")
                
        except Exception as e:
            print(f"Warning: Could not cleanup old backups: {e}")
    
    def list_plan_backups(self) -> List[Dict[str, Any]]:
        """List available plan backups."""
        backup_dir = self.plan_file.parent / 'backups'
        if not backup_dir.exists():
            return []
        
        backups = []
        try:
            backup_files = list(backup_dir.glob('wellness_plan_backup_*.json'))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for backup_file in backup_files:
                try:
                    # Extract timestamp from filename
                    timestamp_str = backup_file.stem.replace('wellness_plan_backup_', '')
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    
                    # Load backup to get plan info
                    with open(backup_file, 'r') as f:
                        backup_plan = json.load(f)
                    
                    backups.append({
                        'filename': backup_file.name,
                        'path': str(backup_file),
                        'created_at': timestamp.isoformat(),
                        'plan_name': backup_plan.get('plan_name', 'Unknown Plan'),
                        'plan_duration': len(backup_plan.get('days', [])),
                        'size_bytes': backup_file.stat().st_size
                    })
                    
                except Exception as e:
                    print(f"Error processing backup {backup_file}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error listing backups: {e}")
        
        return backups
    
    def restore_plan_backup(self, backup_filename: str) -> bool:
        """Restore a plan from backup."""
        backup_dir = self.plan_file.parent / 'backups'
        backup_path = backup_dir / backup_filename
        
        if not backup_path.exists():
            print(f"Backup file not found: {backup_filename}")
            return False
        
        try:
            # Load the backup
            with open(backup_path, 'r') as f:
                backup_plan = json.load(f)
            
            # Add restoration metadata
            backup_plan['restored_at'] = datetime.now().isoformat()
            backup_plan['restored_from'] = backup_filename
            
            # Save as current plan
            with open(self.plan_file, 'w') as f:
                json.dump(backup_plan, f, indent=2)
            
            print(f"Plan restored from backup: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def display_plan_summary(self, plan: Dict[str, Any]) -> None:
        """Display a summary of the wellness plan."""
        print(f"\n=== {plan.get('plan_name', 'Wellness Plan')} ===")
        print(f"Generated: {plan.get('generated_at', 'Unknown')}")
        print(f"Duration: {len(plan.get('days', []))} days\n")
        
        for day in plan.get('days', []):
            print(f"Day {day.get('day', 0)}:")
            activities = day.get('activities', [])
            if not activities:
                print("  Rest day")
            else:
                for activity in activities:
                    duration = activity.get('duration_minutes', 0)
                    activity_type = activity.get('type', '').replace('_', ' ').title()
                    intensity = activity.get('intensity', 'moderate')
                    print(f"  • {activity_type} ({duration} min, {intensity} intensity)")
            
            nutrition = day.get('nutrition', {})
            if nutrition.get('focus'):
                print(f"  Nutrition focus: {nutrition['focus']}")
            print()
    
    def adapt_plan(self, current_plan: Dict[str, Any], progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt the plan based on progress data."""
        print("Adapting plan based on your progress...")
        
        completion_rate = progress_data.get('completion_rate', 0.8)
        missed_activities = progress_data.get('missed_activities', [])
        feedback = progress_data.get('feedback', '')
        
        if completion_rate < 0.5:
            print("Low completion rate detected. Creating easier plan...")
            # Reduce intensity and duration
            for day in current_plan.get('days', []):
                for activity in day.get('activities', []):
                    if activity.get('intensity') == 'high':
                        activity['intensity'] = 'moderate'
                    elif activity.get('intensity') == 'moderate':
                        activity['intensity'] = 'low'
                    
                    # Reduce duration by 25%
                    current_duration = activity.get('duration_minutes', 20)
                    activity['duration_minutes'] = max(10, int(current_duration * 0.75))
        
        elif completion_rate > 0.9:
            print("Great progress! Slightly increasing challenge...")
            # Increase challenge slightly
            for day in current_plan.get('days', []):
                for activity in day.get('activities', []):
                    if activity.get('intensity') == 'low':
                        activity['intensity'] = 'moderate'
                    
                    # Increase duration by 10%
                    current_duration = activity.get('duration_minutes', 20)
                    activity['duration_minutes'] = int(current_duration * 1.1)
        
        # Update generation timestamp
        current_plan['adapted_at'] = datetime.now().isoformat()
        current_plan['adaptation_reason'] = f"Progress rate: {completion_rate:.1%}"
        
        self.save_plan(current_plan)
        print("Plan adapted and saved!")
        return current_plan
    
    def process_chat_update(self, message: str, current_plan: Dict[str, Any], profile: Dict[str, Any], conversation_context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a chat message to update the wellness plan."""
        if not self.client:
            return self._process_chat_fallback(message, current_plan, profile)
        
        # Build context for the AI
        context = self._build_chat_context(message, current_plan, profile, conversation_context)
        
        try:
            print(f"🤖 Processing plan update request: {message[:50]}...")
            response = self.client.chat.completions.create(
                model="grok-beta",
                messages=[{
                    "role": "system",
                    "content": """You are a professional wellness coach AI assistant. You help users modify their existing wellness plans based on their requests. 
                    
                    Your responses should:
                    1. Be conversational and encouraging
                    2. Explain what changes you're making and why
                    3. Suggest improvements when appropriate
                    4. Always prioritize user safety and realistic expectations
                    
                    Return your response as JSON with this structure:
                    {
                        "response": "Your conversational response to the user",
                        "changes_made": ["List of specific changes made"],
                        "plan_modified": true/false,
                        "modified_plan": {...} // The updated plan if modified
                    }
                    
                    If you cannot fulfill the request safely or it's unclear, ask for clarification."""
                }, {
                    "role": "user",
                    "content": context
                }],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_content = response.choices[0].message.content
            
            # Clean up the response to extract JSON
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_content)
            
            # If plan was modified, save it
            if response_data.get('plan_modified') and response_data.get('modified_plan'):
                modified_plan = response_data['modified_plan']
                # Preserve metadata
                modified_plan['generated_at'] = current_plan.get('generated_at')
                modified_plan['profile_snapshot'] = current_plan.get('profile_snapshot')
                modified_plan['last_modified'] = datetime.now().isoformat()
                modified_plan['modification_history'] = current_plan.get('modification_history', [])
                modified_plan['modification_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'request': message,
                    'changes': response_data.get('changes_made', [])
                })
                
                self.save_plan(modified_plan)
                print("Plan updated and saved!")
            
            return {
                'response': response_data.get('response', 'Plan updated successfully!'),
                'proposed_changes': response_data.get('changes_made', []),
                'plan_modified': response_data.get('plan_modified', False)
            }
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {e}")
            return self._process_chat_fallback(message, current_plan, profile)
        except Exception as e:
            print(f"Error processing chat update: {e}")
            return self._process_chat_fallback(message, current_plan, profile)
    
    def _build_chat_context(self, message: str, current_plan: Dict[str, Any], profile: Dict[str, Any], conversation_context: List[Dict[str, Any]] = None) -> str:
        """Build context for the AI chat update request."""
        # Add conversation history if available
        context_intro = ""
        if conversation_context and len(conversation_context) > 0:
            context_intro = "Recent Conversation History:\n"
            for msg in conversation_context[-5:]:  # Last 5 messages for context
                msg_type = "User" if msg.get('type') == 'user' else "AI"
                context_intro += f"{msg_type}: {msg.get('message', '')}\n"
            context_intro += f"\nLatest User Request: \"{message}\"\n\n"
        else:
            context_intro = f"User Request: \"{message}\"\n\n"
        
        # Summarize current plan
        plan_summary = f"Current Plan: {current_plan.get('plan_name', 'Wellness Plan')}\n"
        plan_summary += f"Duration: {len(current_plan.get('days', []))} days\n"
        plan_summary += f"Generated: {current_plan.get('generated_at', 'Unknown')[:10]}\n\n"
        
        # Add day summaries
        plan_summary += "Current Schedule:\n"
        for day in current_plan.get('days', [])[:7]:  # Limit to first 7 days for context
            activities = day.get('activities', [])
            activity_list = []
            for activity in activities:
                duration = activity.get('duration_minutes', 0)
                activity_type = activity.get('type', '').replace('_', ' ').title()
                activity_list.append(f"{activity_type} ({duration}min)")
            
            plan_summary += f"Day {day.get('day', 0)}: {', '.join(activity_list) if activity_list else 'Rest day'}\n"
        
        # Add user preferences context
        user_context = ""
        if profile:
            fitness_level = profile.get('fitness_level', 'unknown')
            goals = profile.get('goals', 'not specified')
            constraints = profile.get('constraints', 'none')
            
            user_context = f"\nUser Profile:\n"
            user_context += f"Fitness Level: {fitness_level}\n"
            user_context += f"Goals: {goals}\n"
            user_context += f"Constraints: {constraints}\n"
            
            activity_prefs = profile.get('activity_preferences', {})
            liked_activities = [k.replace('_', ' ') for k, v in activity_prefs.items() if v]
            if liked_activities:
                user_context += f"Preferred Activities: {', '.join(liked_activities)}\n"
        
        context = f"""{context_intro}{plan_summary}
{user_context}

Please modify the current wellness plan based on the user's request. Consider the conversation history if provided. Make specific, safe changes that align with their fitness level and preferences. If the request is unclear or potentially unsafe, ask for clarification instead of making changes."""
        
        return context
    
    def _process_chat_fallback(self, message: str, current_plan: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback chat processing when AI is not available."""
        print("Processing chat request in fallback mode...")
        
        # Simple keyword-based modifications
        message_lower = message.lower()
        changes_made = []
        plan_modified = False
        
        # Basic intensity modifications
        if any(word in message_lower for word in ['easier', 'reduce', 'less']):
            # Reduce intensity and duration
            for day in current_plan.get('days', []):
                for activity in day.get('activities', []):
                    if activity.get('intensity') == 'high':
                        activity['intensity'] = 'moderate'
                        changes_made.append(f"Reduced {activity.get('type', 'activity')} intensity to moderate")
                        plan_modified = True
                    elif activity.get('intensity') == 'moderate':
                        activity['intensity'] = 'low'
                        changes_made.append(f"Reduced {activity.get('type', 'activity')} intensity to low")
                        plan_modified = True
                    
                    # Reduce duration by 25%
                    current_duration = activity.get('duration_minutes', 20)
                    if current_duration > 10:
                        new_duration = max(10, int(current_duration * 0.75))
                        activity['duration_minutes'] = new_duration
                        changes_made.append(f"Reduced {activity.get('type', 'activity')} duration to {new_duration} minutes")
                        plan_modified = True
        
        elif any(word in message_lower for word in ['harder', 'increase', 'more']):
            # Increase intensity and duration
            for day in current_plan.get('days', []):
                for activity in day.get('activities', []):
                    if activity.get('intensity') == 'low':
                        activity['intensity'] = 'moderate'
                        changes_made.append(f"Increased {activity.get('type', 'activity')} intensity to moderate")
                        plan_modified = True
                    elif activity.get('intensity') == 'moderate':
                        activity['intensity'] = 'high'
                        changes_made.append(f"Increased {activity.get('type', 'activity')} intensity to high")
                        plan_modified = True
                    
                    # Increase duration by 25%
                    current_duration = activity.get('duration_minutes', 20)
                    new_duration = int(current_duration * 1.25)
                    activity['duration_minutes'] = new_duration
                    changes_made.append(f"Increased {activity.get('type', 'activity')} duration to {new_duration} minutes")
                    plan_modified = True
        
        # Save modified plan
        if plan_modified:
            current_plan['last_modified'] = datetime.now().isoformat()
            current_plan['modification_history'] = current_plan.get('modification_history', [])
            current_plan['modification_history'].append({
                'timestamp': datetime.now().isoformat(),
                'request': message,
                'changes': changes_made
            })
            self.save_plan(current_plan)
        
        if not changes_made:
            return {
                'response': "I understand you want to modify your plan, but I need more specific instructions. For example, you could ask me to make workouts easier, add more yoga sessions, or change the duration of activities.",
                'proposed_changes': [],
                'plan_modified': False
            }
        
        response_text = f"I've made the following changes to your wellness plan:\n\n"
        for change in changes_made:
            response_text += f"• {change}\n"
        response_text += f"\nYour plan has been updated and saved. The changes will take effect immediately."
        
        return {
            'response': response_text,
            'proposed_changes': changes_made,
            'plan_modified': plan_modified
        }

if __name__ == "__main__":
    generator = PlanGenerator()
    
    # Test with sample profile
    sample_profile = {
        "age": 30,
        "weight": 70,
        "height": 175,
        "fitness_level": "intermediate",
        "goals": "improve fitness and reduce stress",
        "constraints": "no gym access",
        "available_time_slots": "early morning",
        "activity_preferences": {
            "running": True,
            "yoga": True,
            "meditation": True,
            "strength_training": False
        }
    }
    
    plan = generator.generate_plan(sample_profile)
    generator.display_plan_summary(plan)