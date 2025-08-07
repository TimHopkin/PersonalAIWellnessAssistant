import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PlanGenerator:
    def __init__(self, plan_file: str = "wellness_plan.json"):
        self.plan_file = plan_file
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
        if os.path.exists(self.plan_file):
            try:
                with open(self.plan_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None
        return None
    
    def save_plan(self, plan: Dict[str, Any]) -> None:
        """Save plan to file."""
        with open(self.plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
    
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