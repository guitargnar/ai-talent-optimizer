#!/usr/bin/env python3
"""
Automated Interview Scheduler for Unified Career System
Manages interview scheduling and calendar coordination
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum
import re

# Add parent path
sys.path.append(str(Path(__file__).parent.parent.parent))
from unified_career_system.data_layer.master_database import MasterDatabase
from unified_career_system.response_hub.response_classifier import ResponseType, ResponseClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterviewType(Enum):
    """Types of interviews"""
    PHONE_SCREEN = "phone_screen"
    VIDEO_CALL = "video_call"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    ONSITE = "onsite"
    PANEL = "panel"
    FINAL = "final"


@dataclass
class InterviewSlot:
    """Available time slot for interview"""
    date: datetime
    start_time: time
    end_time: time
    timezone: str = "EST"
    available: bool = True


@dataclass
class InterviewRequest:
    """Interview scheduling request"""
    company: str
    position: str
    interview_type: InterviewType
    duration_minutes: int
    suggested_dates: List[datetime]
    interviewer: Optional[str] = None
    location: Optional[str] = None  # For onsite
    platform: Optional[str] = None  # Zoom, Teams, etc.
    instructions: Optional[str] = None
    email_thread_id: Optional[str] = None


@dataclass
class ScheduledInterview:
    """Confirmed interview details"""
    interview_id: str
    company: str
    position: str
    interview_type: InterviewType
    scheduled_time: datetime
    duration_minutes: int
    interviewer: Optional[str]
    location: Optional[str]
    platform: Optional[str]
    meeting_link: Optional[str]
    preparation_notes: str
    reminder_sent: bool = False


class InterviewScheduler:
    """
    Automated interview scheduling system
    
    Features:
    - Parse interview requests from emails
    - Manage availability calendar
    - Send scheduling responses
    - Create interview prep notes
    - Send reminders
    """
    
    def __init__(self, db_path: str = "unified_career_system/data_layer/unified_career.db"):
        """Initialize the interview scheduler"""
        self.db_path = db_path
        self.master_db = MasterDatabase(db_path)
        self.classifier = ResponseClassifier()
        
        # Default availability windows
        self.availability_windows = self._init_availability()
        
        # Scheduled interviews cache
        self.scheduled_interviews = {}
        self._load_scheduled_interviews()
        
        # Interview preparation templates
        self.prep_templates = self._init_prep_templates()
        
        logger.info("Initialized InterviewScheduler")
        
    def _init_availability(self) -> Dict[str, List[Tuple[time, time]]]:
        """Initialize default availability windows"""
        return {
            'monday': [(time(9, 0), time(12, 0)), (time(13, 0), time(17, 0))],
            'tuesday': [(time(9, 0), time(12, 0)), (time(13, 0), time(17, 0))],
            'wednesday': [(time(9, 0), time(12, 0)), (time(13, 0), time(17, 0))],
            'thursday': [(time(9, 0), time(12, 0)), (time(13, 0), time(17, 0))],
            'friday': [(time(9, 0), time(12, 0)), (time(13, 0), time(16, 0))],
            'saturday': [],  # No availability
            'sunday': []     # No availability
        }
        
    def _init_prep_templates(self) -> Dict[InterviewType, str]:
        """Initialize interview preparation templates"""
        return {
            InterviewType.PHONE_SCREEN: """
📞 Phone Screen Preparation:
1. Review company mission and values
2. Prepare elevator pitch (2-3 minutes)
3. Have resume ready for reference
4. Prepare 3-5 questions about the role
5. Find quiet location with good phone signal
""",
            InterviewType.TECHNICAL: """
💻 Technical Interview Preparation:
1. Review data structures and algorithms
2. Practice coding on whiteboard/shared screen
3. Review recent projects and technical decisions
4. Prepare to explain your ML projects in detail
5. Have development environment ready
6. Review system design basics
""",
            InterviewType.BEHAVIORAL: """
🗣️ Behavioral Interview Preparation:
1. Review STAR method (Situation, Task, Action, Result)
2. Prepare stories for common questions:
   - Challenge overcome
   - Leadership example
   - Conflict resolution
   - Failure and learning
3. Research company culture
4. Prepare questions about team dynamics
""",
            InterviewType.SYSTEM_DESIGN: """
🏗️ System Design Interview Preparation:
1. Review scalability principles
2. Practice drawing architecture diagrams
3. Review ML system design patterns
4. Prepare to discuss:
   - Data pipelines
   - Model serving
   - Monitoring and A/B testing
   - Trade-offs and constraints
""",
            InterviewType.ONSITE: """
🏢 Onsite Interview Preparation:
1. Plan route and arrival (15 min early)
2. Bring multiple copies of resume
3. Dress appropriately (research dress code)
4. Bring notebook and pen
5. Prepare for multiple interview rounds
6. Have references ready
7. Prepare thoughtful questions for each interviewer
""",
            InterviewType.FINAL: """
🎯 Final Interview Preparation:
1. Review all previous interview feedback
2. Prepare to discuss:
   - Salary expectations
   - Start date availability
   - Long-term career goals
3. Have questions about:
   - Growth opportunities
   - Team structure
   - Project roadmap
4. Be ready to express strong interest
"""
        }
        
    def _load_scheduled_interviews(self):
        """Load scheduled interviews from database"""
        cursor = self.master_db.conn.cursor()
        
        # This would load from a dedicated interviews table
        # For now, we'll check application tracking
        cursor.execute("""
        SELECT 
            a.application_uid,
            j.company,
            j.position,
            a.interview_dates
        FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE a.interview_scheduled = 1
        AND a.interview_dates IS NOT NULL
        """)
        
        for row in cursor.fetchall():
            if row[3]:  # interview_dates
                try:
                    dates = json.loads(row[3])
                    for date_str in dates:
                        interview_id = f"{row[0]}_{date_str}"
                        self.scheduled_interviews[interview_id] = {
                            'company': row[1],
                            'position': row[2],
                            'date': datetime.fromisoformat(date_str)
                        }
                except:
                    pass
                    
        logger.info(f"Loaded {len(self.scheduled_interviews)} scheduled interviews")
        
    def parse_interview_request(self, email_body: str, 
                              subject: str,
                              company: str = None) -> Optional[InterviewRequest]:
        """
        Parse interview request from email
        
        Args:
            email_body: Email body text
            subject: Email subject
            company: Company name if known
            
        Returns:
            InterviewRequest if successfully parsed
        """
        # Classify email first
        classification = self.classifier.classify(email_body, subject, company)
        
        # Check if it's an interview request
        interview_types_map = {
            ResponseType.INTERVIEW_PHONE_SCREEN: InterviewType.PHONE_SCREEN,
            ResponseType.INTERVIEW_TECHNICAL: InterviewType.TECHNICAL,
            ResponseType.INTERVIEW_BEHAVIORAL: InterviewType.BEHAVIORAL,
            ResponseType.INTERVIEW_ONSITE: InterviewType.ONSITE,
            ResponseType.INTERVIEW_FINAL: InterviewType.FINAL
        }
        
        if classification.primary_type not in interview_types_map:
            return None
            
        interview_type = interview_types_map[classification.primary_type]
        
        # Extract interview details
        details = self._extract_interview_details(email_body, subject)
        
        if not details:
            return None
            
        return InterviewRequest(
            company=company or details.get('company', 'Unknown'),
            position=details.get('position', 'Unknown Position'),
            interview_type=interview_type,
            duration_minutes=details.get('duration', 60),
            suggested_dates=details.get('dates', []),
            interviewer=details.get('interviewer'),
            location=details.get('location'),
            platform=details.get('platform'),
            instructions=details.get('instructions')
        )
        
    def _extract_interview_details(self, email_body: str, 
                                  subject: str) -> Dict[str, Any]:
        """Extract interview details from email text"""
        details = {}
        text = f"{subject} {email_body}"
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(minutes?|mins?|hours?)', text, re.IGNORECASE)
        if duration_match:
            duration = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            if 'hour' in unit:
                duration *= 60
            details['duration'] = duration
        else:
            details['duration'] = 60  # Default 1 hour
            
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            details['dates'] = dates
            
        # Extract interviewer name
        interviewer_match = re.search(
            r'(with|interviewer:?|meet with)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            text
        )
        if interviewer_match:
            details['interviewer'] = interviewer_match.group(2)
            
        # Extract platform
        platforms = ['zoom', 'teams', 'meet', 'skype', 'webex', 'hangouts']
        for platform in platforms:
            if platform in text.lower():
                details['platform'] = platform.capitalize()
                break
                
        # Extract location for onsite
        if 'onsite' in text.lower() or 'office' in text.lower():
            location_match = re.search(
                r'(at|location:?|address:?)\s+([^,.]+(?:,\s*[^,.]+)?)',
                text, re.IGNORECASE
            )
            if location_match:
                details['location'] = location_match.group(2).strip()
                
        # Extract position if mentioned
        position_match = re.search(
            r'(position|role|job):?\s*([^,.]+)',
            text, re.IGNORECASE
        )
        if position_match:
            details['position'] = position_match.group(2).strip()
            
        return details
        
    def _extract_dates(self, text: str) -> List[datetime]:
        """Extract suggested dates from text"""
        dates = []
        
        # Look for specific date patterns
        # Format: Monday, January 15
        date_pattern = r'(Monday|Tuesday|Wednesday|Thursday|Friday),?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})'
        
        for match in re.finditer(date_pattern, text, re.IGNORECASE):
            try:
                date_str = match.group()
                # Parse date (simplified - in production use dateutil)
                # For now, assume current year
                parsed_date = datetime.strptime(
                    f"{date_str} {datetime.now().year}",
                    "%A, %B %d %Y"
                )
                dates.append(parsed_date)
            except:
                pass
                
        # Look for relative dates
        if 'tomorrow' in text.lower():
            dates.append(datetime.now() + timedelta(days=1))
        if 'this week' in text.lower():
            # Add next 5 days as options
            for i in range(1, 6):
                dates.append(datetime.now() + timedelta(days=i))
                
        return dates
        
    def find_available_slots(self, request: InterviewRequest,
                           days_ahead: int = 14) -> List[InterviewSlot]:
        """
        Find available time slots for interview
        
        Args:
            request: Interview request details
            days_ahead: Number of days to look ahead
            
        Returns:
            List of available time slots
        """
        available_slots = []
        current_date = datetime.now().date()
        
        for day_offset in range(days_ahead):
            check_date = current_date + timedelta(days=day_offset)
            weekday = check_date.strftime('%A').lower()
            
            # Skip weekends if no availability
            if weekday in self.availability_windows:
                windows = self.availability_windows[weekday]
                
                for start_time, end_time in windows:
                    # Check if slot is long enough for interview
                    slot_duration = (
                        datetime.combine(check_date, end_time) -
                        datetime.combine(check_date, start_time)
                    ).total_seconds() / 60
                    
                    if slot_duration >= request.duration_minutes:
                        # Check if slot conflicts with existing interviews
                        slot_datetime = datetime.combine(check_date, start_time)
                        
                        if not self._has_conflict(slot_datetime, request.duration_minutes):
                            available_slots.append(InterviewSlot(
                                date=check_date,
                                start_time=start_time,
                                end_time=end_time,
                                available=True
                            ))
                            
        # Prioritize suggested dates if provided
        if request.suggested_dates:
            prioritized = []
            for suggested in request.suggested_dates:
                for slot in available_slots:
                    if slot.date == suggested.date():
                        prioritized.append(slot)
                        
            # Add remaining slots
            for slot in available_slots:
                if slot not in prioritized:
                    prioritized.append(slot)
                    
            return prioritized[:10]  # Return top 10 slots
            
        return available_slots[:10]
        
    def _has_conflict(self, slot_time: datetime, duration_minutes: int) -> bool:
        """Check if time slot conflicts with existing interviews"""
        slot_end = slot_time + timedelta(minutes=duration_minutes)
        
        for interview_id, details in self.scheduled_interviews.items():
            interview_time = details['date']
            # Assume 1 hour duration if not specified
            interview_end = interview_time + timedelta(hours=1)
            
            # Check for overlap
            if (slot_time < interview_end and slot_end > interview_time):
                return True
                
        return False
        
    def schedule_interview(self, request: InterviewRequest,
                         selected_slot: InterviewSlot) -> ScheduledInterview:
        """
        Schedule an interview
        
        Args:
            request: Interview request details
            selected_slot: Selected time slot
            
        Returns:
            ScheduledInterview object
        """
        # Generate interview ID
        interview_id = f"{request.company}_{selected_slot.date}_{selected_slot.start_time}".replace(' ', '_')
        
        # Create scheduled interview
        scheduled = ScheduledInterview(
            interview_id=interview_id,
            company=request.company,
            position=request.position,
            interview_type=request.interview_type,
            scheduled_time=datetime.combine(selected_slot.date, selected_slot.start_time),
            duration_minutes=request.duration_minutes,
            interviewer=request.interviewer,
            location=request.location,
            platform=request.platform,
            meeting_link=None,  # Would be in confirmation email
            preparation_notes=self._generate_prep_notes(request),
            reminder_sent=False
        )
        
        # Store in database
        self._store_scheduled_interview(scheduled)
        
        # Add to cache
        self.scheduled_interviews[interview_id] = {
            'company': request.company,
            'position': request.position,
            'date': scheduled.scheduled_time,
            'type': request.interview_type.value
        }
        
        logger.info(f"Scheduled {request.interview_type.value} interview with {request.company}")
        
        return scheduled
        
    def _generate_prep_notes(self, request: InterviewRequest) -> str:
        """Generate preparation notes for interview"""
        base_notes = self.prep_templates.get(
            request.interview_type,
            "Review company information and prepare questions."
        )
        
        # Add company-specific notes
        custom_notes = f"\n📍 Company: {request.company}\n"
        custom_notes += f"📋 Position: {request.position}\n"
        
        if request.interviewer:
            custom_notes += f"👤 Interviewer: {request.interviewer}\n"
            custom_notes += "   - Look up on LinkedIn\n"
            custom_notes += "   - Find common connections/interests\n"
            
        if request.platform:
            custom_notes += f"💻 Platform: {request.platform}\n"
            custom_notes += "   - Test audio/video beforehand\n"
            custom_notes += "   - Have backup contact method\n"
            
        if request.location:
            custom_notes += f"📍 Location: {request.location}\n"
            custom_notes += "   - Plan route and parking\n"
            custom_notes += "   - Arrive 15 minutes early\n"
            
        return base_notes + custom_notes
        
    def _store_scheduled_interview(self, interview: ScheduledInterview):
        """Store scheduled interview in database"""
        cursor = self.master_db.conn.cursor()
        
        # Find related application
        cursor.execute("""
        SELECT a.application_uid
        FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE j.company = ?
        AND j.position = ?
        ORDER BY a.applied_date DESC
        LIMIT 1
        """, (interview.company, interview.position))
        
        result = cursor.fetchone()
        
        if result:
            app_uid = result[0]
            
            # Update application with interview details
            cursor.execute("""
            UPDATE master_applications
            SET interview_scheduled = 1,
                interview_dates = ?,
                interview_rounds = interview_rounds + 1,
                interview_notes = ?
            WHERE application_uid = ?
            """, (
                json.dumps([interview.scheduled_time.isoformat()]),
                interview.preparation_notes,
                app_uid
            ))
            
            self.master_db.conn.commit()
            
    def generate_response_email(self, request: InterviewRequest,
                              selected_slots: List[InterviewSlot]) -> str:
        """
        Generate response email for interview scheduling
        
        Args:
            request: Interview request
            selected_slots: Available time slots
            
        Returns:
            Email body text
        """
        email = f"""Dear {request.company} Team,

Thank you for the opportunity to interview for the {request.position} position. 
I'm very excited to discuss how my experience can contribute to your team.

I am available for a {request.interview_type.value.replace('_', ' ')} interview 
at the following times (EST):

"""
        
        # Add available slots
        for i, slot in enumerate(selected_slots[:5], 1):
            date_str = slot.date.strftime('%A, %B %d')
            time_str = slot.start_time.strftime('%-I:%M %p')
            email += f"{i}. {date_str} at {time_str}\n"
            
        email += """
Please let me know which time works best for your team, and I'll make sure 
to block my calendar accordingly.

"""
        
        if request.platform:
            email += f"I'll be ready to connect via {request.platform}. "
        elif request.location:
            email += f"I look forward to visiting your office at {request.location}. "
            
        email += """

Looking forward to our conversation!

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
"""
        
        return email
        
    def send_reminders(self, hours_before: int = 24):
        """
        Send reminders for upcoming interviews
        
        Args:
            hours_before: Hours before interview to send reminder
        """
        reminder_time = datetime.now() + timedelta(hours=hours_before)
        
        for interview_id, details in self.scheduled_interviews.items():
            interview_time = details['date']
            
            # Check if reminder should be sent
            if (interview_time > datetime.now() and 
                interview_time <= reminder_time and
                not details.get('reminder_sent', False)):
                
                # Send reminder
                self._send_interview_reminder(interview_id, details)
                
                # Mark as sent
                self.scheduled_interviews[interview_id]['reminder_sent'] = True
                
    def _send_interview_reminder(self, interview_id: str, details: Dict):
        """Send interview reminder"""
        time_until = details['date'] - datetime.now()
        hours = int(time_until.total_seconds() / 3600)
        
        logger.info(f"""
🔔 Interview Reminder:
Company: {details['company']}
Position: {details['position']}
Time: {details['date'].strftime('%B %d at %-I:%M %p')}
In: {hours} hours

Remember to:
- Review preparation notes
- Test technology (if virtual)
- Prepare questions
- Review resume and projects
""")
        
    def get_upcoming_interviews(self, days_ahead: int = 7) -> List[Dict]:
        """Get list of upcoming interviews"""
        upcoming = []
        cutoff = datetime.now() + timedelta(days=days_ahead)
        
        for interview_id, details in self.scheduled_interviews.items():
            if datetime.now() < details['date'] <= cutoff:
                upcoming.append({
                    'id': interview_id,
                    'company': details['company'],
                    'position': details['position'],
                    'date': details['date'],
                    'type': details.get('type', 'unknown')
                })
                
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        
        return upcoming


def main():
    """Test the interview scheduler"""
    scheduler = InterviewScheduler()
    
    print("📅 Interview Scheduler v1.0")
    print("=" * 60)
    
    # Test parsing interview request
    test_email = """
    Hi Matthew,
    
    We were impressed with your application and would like to schedule
    a technical interview with our ML team lead, Sarah Johnson.
    
    The interview will be 60 minutes via Zoom. Are you available
    this Tuesday, January 15 or Thursday, January 17?
    
    Please let us know your availability.
    
    Best,
    TechCorp Recruiting
    """
    
    print("\n📧 Parsing Interview Request:")
    print("=" * 60)
    
    request = scheduler.parse_interview_request(
        test_email,
        "Technical Interview - ML Engineer Position",
        "TechCorp"
    )
    
    if request:
        print(f"✅ Successfully parsed interview request:")
        print(f"  Company: {request.company}")
        print(f"  Position: {request.position}")
        print(f"  Type: {request.interview_type.value}")
        print(f"  Duration: {request.duration_minutes} minutes")
        print(f"  Interviewer: {request.interviewer or 'Not specified'}")
        print(f"  Platform: {request.platform or 'Not specified'}")
        
        # Find available slots
        print("\n🔍 Finding Available Slots:")
        slots = scheduler.find_available_slots(request)
        
        print(f"Found {len(slots)} available slots:")
        for i, slot in enumerate(slots[:5], 1):
            print(f"  {i}. {slot.date.strftime('%A, %B %d')} at {slot.start_time.strftime('%-I:%M %p')}")
            
        # Generate response email
        print("\n✉️ Generated Response Email:")
        print("-" * 40)
        response = scheduler.generate_response_email(request, slots)
        print(response)
        
        # Schedule interview (simulate)
        if slots:
            scheduled = scheduler.schedule_interview(request, slots[0])
            print("\n✅ Interview Scheduled:")
            print(f"  ID: {scheduled.interview_id}")
            print(f"  Time: {scheduled.scheduled_time}")
            
            print("\n📝 Preparation Notes:")
            print(scheduled.preparation_notes)
    else:
        print("❌ Could not parse interview request")
        
    # Show upcoming interviews
    print("\n📅 Upcoming Interviews:")
    upcoming = scheduler.get_upcoming_interviews()
    
    if upcoming:
        for interview in upcoming:
            print(f"  • {interview['date'].strftime('%b %d')}: {interview['company']} - {interview['type']}")
    else:
        print("  No upcoming interviews scheduled")
        
    print("\n✨ Interview scheduler test complete!")


if __name__ == "__main__":
    main()