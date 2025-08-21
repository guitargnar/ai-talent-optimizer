#!/usr/bin/env python3
"""
ML-Powered Response Classifier for Unified Career System
Uses NLP and pattern matching to accurately classify email responses
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Detailed response classifications"""
    # Positive responses
    INTERVIEW_PHONE_SCREEN = "interview_phone_screen"
    INTERVIEW_TECHNICAL = "interview_technical" 
    INTERVIEW_BEHAVIORAL = "interview_behavioral"
    INTERVIEW_ONSITE = "interview_onsite"
    INTERVIEW_FINAL = "interview_final"
    OFFER_VERBAL = "offer_verbal"
    OFFER_WRITTEN = "offer_written"
    
    # Neutral responses
    APPLICATION_RECEIVED = "application_received"
    UNDER_REVIEW = "under_review"
    INFORMATION_REQUEST = "information_request"
    REFERENCE_CHECK = "reference_check"
    BACKGROUND_CHECK = "background_check"
    
    # Negative responses
    REJECTION_GENERIC = "rejection_generic"
    REJECTION_NOT_QUALIFIED = "rejection_not_qualified"
    REJECTION_OVERQUALIFIED = "rejection_overqualified"
    REJECTION_POSITION_FILLED = "rejection_position_filled"
    REJECTION_NOT_CULTURE_FIT = "rejection_not_culture_fit"
    
    # Other
    AUTO_REPLY = "auto_reply"
    FOLLOW_UP = "follow_up"
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    """Result of email classification"""
    primary_type: ResponseType
    confidence: float
    sentiment: float  # -1 (negative) to 1 (positive)
    urgency: str  # low, medium, high, critical
    key_phrases: List[str]
    action_required: bool
    suggested_action: Optional[str]
    deadline_days: Optional[int]


class ResponseClassifier:
    """
    Advanced email response classifier using ML techniques
    
    Features:
    - Multi-level classification hierarchy
    - Confidence scoring
    - Sentiment analysis
    - Urgency detection
    - Action extraction
    """
    
    def __init__(self):
        """Initialize the response classifier"""
        # Pattern definitions with weights
        self.patterns = self._init_patterns()
        
        # Sentiment indicators
        self.sentiment_patterns = self._init_sentiment_patterns()
        
        # Urgency indicators
        self.urgency_patterns = self._init_urgency_patterns()
        
        # Action keywords
        self.action_keywords = self._init_action_keywords()
        
        # Company-specific patterns (learned over time)
        self.company_patterns = {}
        self._load_company_patterns()
        
        logger.info("Initialized ResponseClassifier with ML patterns")
        
    def _init_patterns(self) -> Dict[ResponseType, List[Tuple[str, float]]]:
        """Initialize classification patterns with confidence weights"""
        return {
            # Interview patterns
            ResponseType.INTERVIEW_PHONE_SCREEN: [
                (r'phone\s+(screen|interview|call)', 0.9),
                (r'initial\s+(phone|conversation|chat)', 0.85),
                (r'brief\s+call', 0.8),
                (r'15-30\s+minute', 0.75),
                (r'recruiter\s+call', 0.85)
            ],
            ResponseType.INTERVIEW_TECHNICAL: [
                (r'technical\s+(interview|assessment|challenge)', 0.95),
                (r'coding\s+(challenge|interview|test)', 0.95),
                (r'take[- ]home\s+(assignment|project)', 0.9),
                (r'leetcode|hackerrank|codility', 0.9),
                (r'system\s+design', 0.85)
            ],
            ResponseType.INTERVIEW_BEHAVIORAL: [
                (r'behavioral\s+interview', 0.95),
                (r'culture\s+fit', 0.85),
                (r'meet\s+the\s+team', 0.8),
                (r'panel\s+interview', 0.85),
                (r'hiring\s+manager', 0.8)
            ],
            ResponseType.INTERVIEW_ONSITE: [
                (r'on[- ]?site\s+interview', 0.95),
                (r'come\s+to\s+our\s+office', 0.9),
                (r'full[- ]day\s+interview', 0.9),
                (r'visit\s+our\s+(office|campus)', 0.85),
                (r'final\s+round', 0.8)
            ],
            
            # Offer patterns
            ResponseType.OFFER_VERBAL: [
                (r'verbal\s+offer', 0.95),
                (r'pleased\s+to\s+offer', 0.9),
                (r'congratulations.*position', 0.85),
                (r'would\s+like\s+to\s+extend', 0.85),
                (r'excited\s+to\s+offer', 0.9)
            ],
            ResponseType.OFFER_WRITTEN: [
                (r'offer\s+letter', 0.95),
                (r'formal\s+offer', 0.9),
                (r'compensation\s+package', 0.85),
                (r'salary.*benefits', 0.8),
                (r'start\s+date', 0.75)
            ],
            
            # Rejection patterns
            ResponseType.REJECTION_GENERIC: [
                (r'unfortunately', 0.8),
                (r'not\s+moving\s+forward', 0.9),
                (r'decided\s+not\s+to\s+proceed', 0.9),
                (r'not\s+selected', 0.85),
                (r'pursuing\s+other\s+candidates', 0.85)
            ],
            ResponseType.REJECTION_NOT_QUALIFIED: [
                (r'not\s+meet.*requirements', 0.9),
                (r'looking\s+for.*more\s+experience', 0.85),
                (r'skill\s+set.*not\s+match', 0.85),
                (r'qualifications.*not\s+align', 0.85)
            ],
            ResponseType.REJECTION_OVERQUALIFIED: [
                (r'overqualified', 0.95),
                (r'too\s+senior', 0.9),
                (r'exceed.*requirements', 0.8),
                (r'more\s+junior', 0.85)
            ],
            ResponseType.REJECTION_POSITION_FILLED: [
                (r'position.*filled', 0.95),
                (r'role.*no\s+longer', 0.9),
                (r'hired\s+another', 0.85),
                (r'position.*closed', 0.9)
            ],
            
            # Neutral patterns
            ResponseType.APPLICATION_RECEIVED: [
                (r'received\s+your\s+application', 0.95),
                (r'thank\s+you\s+for\s+applying', 0.9),
                (r'application.*submitted', 0.85),
                (r'confirming\s+receipt', 0.85)
            ],
            ResponseType.UNDER_REVIEW: [
                (r'reviewing\s+your\s+application', 0.9),
                (r'under\s+review', 0.95),
                (r'being\s+considered', 0.85),
                (r'evaluation\s+process', 0.8),
                (r'reviewing\s+candidates', 0.85)
            ],
            ResponseType.INFORMATION_REQUEST: [
                (r'please\s+provide', 0.9),
                (r'could\s+you\s+send', 0.85),
                (r'additional\s+information', 0.85),
                (r'need.*documents', 0.8),
                (r'complete.*form', 0.85)
            ],
            
            # Auto-reply patterns
            ResponseType.AUTO_REPLY: [
                (r'auto[- ]?reply', 0.95),
                (r'automatic\s+response', 0.95),
                (r'do\s+not\s+reply', 0.9),
                (r'no[- ]?reply@', 0.9),
                (r'automated\s+message', 0.9)
            ]
        }
        
    def _init_sentiment_patterns(self) -> Dict[str, List[str]]:
        """Initialize sentiment analysis patterns"""
        return {
            'positive': [
                'impressed', 'excited', 'pleased', 'excellent', 'outstanding',
                'strong', 'perfect', 'ideal', 'great fit', 'love to',
                'looking forward', 'congratulations', 'welcome'
            ],
            'negative': [
                'unfortunately', 'regret', 'sorry', 'unable', 'not',
                'cannot', 'won\'t', 'decided against', 'other direction',
                'not a match', 'doesn\'t align', 'concerns'
            ],
            'neutral': [
                'review', 'consider', 'evaluate', 'process', 'received',
                'thank you', 'acknowledge', 'confirm', 'update'
            ]
        }
        
    def _init_urgency_patterns(self) -> Dict[str, List[str]]:
        """Initialize urgency detection patterns"""
        return {
            'critical': [
                'urgent', 'asap', 'immediately', 'today', 'expires',
                'final notice', 'last chance', 'deadline today'
            ],
            'high': [
                'soon', 'quickly', 'priority', 'by tomorrow',
                'within 24 hours', 'time-sensitive', 'expedite'
            ],
            'medium': [
                'within a week', 'few days', 'when convenient',
                'at your earliest', 'please respond'
            ],
            'low': [
                'no rush', 'when you can', 'future', 'eventually',
                'keep in touch', 'stay connected'
            ]
        }
        
    def _init_action_keywords(self) -> Dict[str, List[str]]:
        """Initialize action extraction keywords"""
        return {
            'schedule': [
                'schedule', 'book', 'calendar', 'availability',
                'time slots', 'convenient time', 'set up'
            ],
            'provide': [
                'send', 'provide', 'submit', 'share', 'upload',
                'complete', 'fill out', 'attach'
            ],
            'confirm': [
                'confirm', 'verify', 'acknowledge', 'accept',
                'let us know', 'reply', 'respond'
            ],
            'review': [
                'review', 'consider', 'evaluate', 'look over',
                'examine', 'study', 'go through'
            ]
        }
        
    def _load_company_patterns(self):
        """Load learned company-specific patterns"""
        # In production, this would load from a trained model or database
        # For now, we'll use some common patterns
        self.company_patterns = {
            'google': {
                'interview_style': 'technical_heavy',
                'response_time': 'fast',
                'keywords': ['googley', 'scalability', 'algorithms']
            },
            'startup': {
                'interview_style': 'practical',
                'response_time': 'variable',
                'keywords': ['culture fit', 'wear many hats', 'fast-paced']
            }
        }
        
    def classify(self, email_text: str, subject: str = "",
                company: str = None) -> ClassificationResult:
        """
        Classify an email response using ML techniques
        
        Args:
            email_text: Body of the email
            subject: Email subject line
            company: Company name (optional, for company-specific patterns)
            
        Returns:
            ClassificationResult with detailed analysis
        """
        # Combine subject and body for analysis
        full_text = f"{subject} {email_text}".lower()
        
        # Score each response type
        type_scores = {}
        matched_phrases = []
        
        for response_type, patterns in self.patterns.items():
            score = 0.0
            for pattern, weight in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    score += weight
                    # Extract matched phrase
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        matched_phrases.append(match.group())
                        
            type_scores[response_type] = score
            
        # Get primary classification
        if type_scores:
            primary_type = max(type_scores, key=type_scores.get)
            confidence = min(type_scores[primary_type] / 2.0, 1.0)  # Normalize confidence
        else:
            primary_type = ResponseType.UNKNOWN
            confidence = 0.0
            
        # Calculate sentiment
        sentiment = self._analyze_sentiment(full_text)
        
        # Detect urgency
        urgency = self._detect_urgency(full_text)
        
        # Check if action required
        action_required, suggested_action = self._extract_action(full_text, primary_type)
        
        # Estimate deadline
        deadline_days = self._estimate_deadline(full_text, urgency, primary_type)
        
        # Apply company-specific adjustments
        if company and company.lower() in self.company_patterns:
            confidence = self._apply_company_patterns(
                company.lower(), primary_type, confidence
            )
            
        return ClassificationResult(
            primary_type=primary_type,
            confidence=confidence,
            sentiment=sentiment,
            urgency=urgency,
            key_phrases=list(set(matched_phrases))[:5],  # Top 5 unique phrases
            action_required=action_required,
            suggested_action=suggested_action,
            deadline_days=deadline_days
        )
        
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of the text"""
        positive_count = sum(
            1 for word in self.sentiment_patterns['positive']
            if word in text.lower()
        )
        negative_count = sum(
            1 for word in self.sentiment_patterns['negative']
            if word in text.lower()
        )
        neutral_count = sum(
            1 for word in self.sentiment_patterns['neutral']
            if word in text.lower()
        )
        
        total = positive_count + negative_count + neutral_count
        
        if total == 0:
            return 0.0
            
        # Calculate weighted sentiment
        sentiment = (positive_count - negative_count) / total
        
        return max(-1.0, min(1.0, sentiment))
        
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level of the email"""
        text_lower = text.lower()
        
        for level in ['critical', 'high', 'medium', 'low']:
            for keyword in self.urgency_patterns[level]:
                if keyword in text_lower:
                    return level
                    
        # Check for dates
        if re.search(r'\b(today|tonight|tomorrow|monday|tuesday|wednesday|thursday|friday)\b', 
                    text_lower):
            return 'high'
        elif re.search(r'\b(this week|next week)\b', text_lower):
            return 'medium'
            
        return 'low'
        
    def _extract_action(self, text: str, 
                       response_type: ResponseType) -> Tuple[bool, Optional[str]]:
        """Extract required action from email"""
        text_lower = text.lower()
        
        # Check for explicit action requests
        for action_type, keywords in self.action_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Map to specific action based on response type
                    if response_type in [ResponseType.INTERVIEW_PHONE_SCREEN,
                                        ResponseType.INTERVIEW_TECHNICAL,
                                        ResponseType.INTERVIEW_BEHAVIORAL,
                                        ResponseType.INTERVIEW_ONSITE]:
                        return True, f"{action_type}_interview"
                    elif response_type == ResponseType.INFORMATION_REQUEST:
                        return True, f"{action_type}_information"
                    elif response_type in [ResponseType.OFFER_VERBAL,
                                          ResponseType.OFFER_WRITTEN]:
                        return True, f"{action_type}_offer"
                    else:
                        return True, action_type
                        
        # No explicit action found
        if response_type in [ResponseType.INTERVIEW_PHONE_SCREEN,
                            ResponseType.INTERVIEW_TECHNICAL,
                            ResponseType.INTERVIEW_BEHAVIORAL,
                            ResponseType.INTERVIEW_ONSITE,
                            ResponseType.INFORMATION_REQUEST,
                            ResponseType.OFFER_VERBAL,
                            ResponseType.OFFER_WRITTEN]:
            return True, "respond_required"
            
        return False, None
        
    def _estimate_deadline(self, text: str, urgency: str,
                         response_type: ResponseType) -> Optional[int]:
        """Estimate deadline in days for response"""
        # Check for explicit deadlines
        deadline_match = re.search(
            r'(within|by|before)\s+(\d+)\s+(day|business day|week)',
            text, re.IGNORECASE
        )
        
        if deadline_match:
            number = int(deadline_match.group(2))
            unit = deadline_match.group(3).lower()
            
            if 'week' in unit:
                return number * 7
            else:
                return number
                
        # Use defaults based on urgency and type
        if urgency == 'critical':
            return 1
        elif urgency == 'high':
            return 2
        elif response_type in [ResponseType.INTERVIEW_PHONE_SCREEN,
                              ResponseType.INTERVIEW_TECHNICAL]:
            return 3
        elif response_type in [ResponseType.OFFER_VERBAL,
                              ResponseType.OFFER_WRITTEN]:
            return 5
        elif urgency == 'medium':
            return 7
        else:
            return None
            
    def _apply_company_patterns(self, company: str,
                               response_type: ResponseType,
                               confidence: float) -> float:
        """Apply company-specific pattern adjustments"""
        if company in self.company_patterns:
            patterns = self.company_patterns[company]
            
            # Adjust confidence based on company patterns
            if patterns.get('interview_style') == 'technical_heavy':
                if response_type == ResponseType.INTERVIEW_TECHNICAL:
                    confidence *= 1.1  # Boost confidence for technical interviews
                    
            # Add more company-specific adjustments as needed
            
        return min(confidence, 1.0)
        
    def learn_from_feedback(self, email_text: str, subject: str,
                           actual_type: ResponseType, was_correct: bool):
        """
        Learn from classification feedback (for future ML model training)
        
        Args:
            email_text: Original email text
            subject: Original subject
            actual_type: The correct classification
            was_correct: Whether our classification was correct
        """
        # In production, this would update model weights or retrain
        # For now, we'll just log for analysis
        logger.info(f"Feedback: Type={actual_type.value}, Correct={was_correct}")
        
        if not was_correct:
            # Extract patterns from misclassified email for future improvement
            logger.warning(f"Misclassification: Review patterns for {actual_type.value}")
            
    def get_classification_confidence(self, result: ClassificationResult) -> str:
        """Get human-readable confidence level"""
        if result.confidence >= 0.9:
            return "Very High"
        elif result.confidence >= 0.7:
            return "High"
        elif result.confidence >= 0.5:
            return "Medium"
        elif result.confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"


def main():
    """Test the response classifier"""
    classifier = ResponseClassifier()
    
    print("🤖 ML Response Classifier v1.0")
    print("=" * 60)
    
    # Test emails
    test_emails = [
        {
            'subject': 'Re: Machine Learning Engineer Application',
            'body': """Thank you for your interest in the ML Engineer position at TechCorp.
                      We were impressed with your background and would like to schedule
                      a phone screen with our recruiter. Please let us know your availability
                      for a 30-minute call this week.""",
            'company': 'TechCorp'
        },
        {
            'subject': 'Your Application to StartupAI',
            'body': """Unfortunately, we have decided not to move forward with your application
                      at this time. We were looking for someone with more experience in
                      computer vision specifically. We wish you the best in your search.""",
            'company': 'StartupAI'
        },
        {
            'subject': 'Congratulations! Job Offer from DataCo',
            'body': """We are pleased to extend you an offer for the Senior ML Engineer position.
                      The compensation package includes a base salary of $180,000 plus equity.
                      Please review the attached offer letter and let us know if you accept.""",
            'company': 'DataCo'
        },
        {
            'subject': 'Application Received',
            'body': """This is an automated message to confirm we have received your application
                      for the ML Engineer position. Our team will review your application and
                      contact you if we decide to move forward. Do not reply to this email.""",
            'company': None
        }
    ]
    
    print("\n🧪 Testing Email Classification:")
    print("=" * 60)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Email {i}: {email['subject']}")
        print(f"Company: {email.get('company', 'Unknown')}")
        print(f"Body preview: {email['body'][:100]}...")
        
        # Classify email
        result = classifier.classify(
            email['body'],
            email['subject'],
            email.get('company')
        )
        
        print(f"\n📊 Classification Result:")
        print(f"  Type: {result.primary_type.value}")
        print(f"  Confidence: {result.confidence:.2%} ({classifier.get_classification_confidence(result)})")
        print(f"  Sentiment: {result.sentiment:+.2f}")
        print(f"  Urgency: {result.urgency}")
        print(f"  Action Required: {'Yes' if result.action_required else 'No'}")
        
        if result.suggested_action:
            print(f"  Suggested Action: {result.suggested_action}")
        if result.deadline_days:
            print(f"  Deadline: {result.deadline_days} days")
        if result.key_phrases:
            print(f"  Key Phrases: {', '.join(result.key_phrases[:3])}")
            
    print("\n✨ Response classifier test complete!")


if __name__ == "__main__":
    main()