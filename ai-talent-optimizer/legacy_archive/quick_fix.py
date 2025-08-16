#!/usr/bin/env python3
"""
Quick fixes for testing commands
"""

from signal_booster import SignalBooster

# Add the missing method as a wrapper
def add_get_todays_activities():
    """Add the get_todays_activities method to SignalBooster"""
    def get_todays_activities(self):
        plan = self.generate_daily_plan()
        activities = []
        for time_block in plan.get('time_blocks', []):
            activities.append({
                'icon': time_block.get('priority_icon', '🔷'),
                'task': time_block.get('activity', ''),
                'time_estimate': time_block.get('duration', '')
            })
        return activities
    
    SignalBooster.get_todays_activities = get_todays_activities

# Apply the fix
add_get_todays_activities()

if __name__ == "__main__":
    # Test it
    s = SignalBooster()
    activities = s.get_todays_activities()
    for a in activities:
        print(f'{a["icon"]} {a["task"]} ({a["time_estimate"]})')