#!/usr/bin/env python3
"""
Setup Scheduler for AI Job Hunter
Creates launchd configuration for macOS to run at 9am and 6pm daily
"""

import os
import subprocess
from pathlib import Path
import pwd


class SchedulerSetup:
    """Setup automated scheduling for AI Job Hunter"""
    
    def __init__(self):
        self.base_dir = Path("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer")
        self.user = pwd.getpwuid(os.getuid()).pw_name
        self.launch_agents_dir = Path(f"/Users/{self.user}/Library/LaunchAgents")
        
    def create_launchd_plist(self):
        """Create launchd plist file for scheduling"""
        
        # Morning job (9 AM)
        morning_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.matthewscott.aijobhunter.morning</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{self.base_dir}/run_automation.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.base_dir}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{self.base_dir}/logs/morning_run.log</string>
    <key>StandardErrorPath</key>
    <string>{self.base_dir}/logs/morning_run_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>"""

        # Evening job (6 PM)
        evening_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.matthewscott.aijobhunter.evening</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{self.base_dir}/run_automation.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.base_dir}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{self.base_dir}/logs/evening_run.log</string>
    <key>StandardErrorPath</key>
    <string>{self.base_dir}/logs/evening_run_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>"""

        # Create logs directory
        logs_dir = self.base_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Save plist files
        morning_path = self.launch_agents_dir / "com.matthewscott.aijobhunter.morning.plist"
        evening_path = self.launch_agents_dir / "com.matthewscott.aijobhunter.evening.plist"
        
        with open(morning_path, 'w') as f:
            f.write(morning_plist)
        
        with open(evening_path, 'w') as f:
            f.write(evening_plist)
        
        print(f"✅ Created launchd plists:")
        print(f"   • {morning_path}")
        print(f"   • {evening_path}")
        
        return morning_path, evening_path
    
    def load_launchd_jobs(self, morning_path, evening_path):
        """Load the launchd jobs"""
        print("\n🔧 Loading launchd jobs...")
        
        # Unload if already loaded
        for label in ["com.matthewscott.aijobhunter.morning", "com.matthewscott.aijobhunter.evening"]:
            subprocess.run(['launchctl', 'unload', '-w', f"{self.launch_agents_dir}/{label}.plist"], 
                         capture_output=True)
        
        # Load the jobs
        for path in [morning_path, evening_path]:
            result = subprocess.run(['launchctl', 'load', '-w', str(path)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Loaded: {path.name}")
            else:
                print(f"❌ Failed to load {path.name}: {result.stderr}")
    
    def create_manual_run_script(self):
        """Create a script for manual runs"""
        script_path = self.base_dir / "run_now.sh"
        
        script_content = f"""#!/bin/bash
# Manual run script for AI Job Hunter

cd {self.base_dir}

echo "🚀 AI Job Hunter - Manual Run"
echo "============================="
echo ""

# Activate virtual environment if it exists
if [ -f "google-env/bin/activate" ]; then
    source google-env/bin/activate
fi

# Run the automation
python3 run_automation.py

echo ""
echo "✅ Manual run complete!"
"""
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"\n✅ Created manual run script: {script_path}")
        print("   Run with: ./run_now.sh")
    
    def show_status(self):
        """Show scheduler status"""
        print("\n📊 Scheduler Status")
        print("=" * 60)
        
        result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if 'aijobhunter' in line:
                print(line)
        
        print("\n💡 Useful commands:")
        print("   • Start now: launchctl start com.matthewscott.aijobhunter.morning")
        print("   • Stop: launchctl stop com.matthewscott.aijobhunter.morning")
        print("   • View logs: tail -f logs/morning_run.log")
    
    def setup_complete_scheduler(self):
        """Complete scheduler setup"""
        print("🤖 AI Job Hunter Scheduler Setup")
        print("=" * 60)
        
        # Create launchd plists
        morning_path, evening_path = self.create_launchd_plist()
        
        # Load the jobs
        self.load_launchd_jobs(morning_path, evening_path)
        
        # Create manual run script
        self.create_manual_run_script()
        
        # Show status
        self.show_status()
        
        print("\n✅ Scheduler setup complete!")
        print("\n📅 Scheduled runs:")
        print("   • 9:00 AM daily - Morning job discovery and applications")
        print("   • 6:00 PM daily - Evening job discovery and applications")
        
        print("\n🎯 Test the setup:")
        print("   1. Manual test: ./run_now.sh")
        print("   2. Trigger morning job: launchctl start com.matthewscott.aijobhunter.morning")
        print("   3. Check logs: tail -f logs/morning_run.log")


def main():
    """Main setup function"""
    setup = SchedulerSetup()
    setup.setup_complete_scheduler()


if __name__ == "__main__":
    main()