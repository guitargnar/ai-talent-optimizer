"""
Unified database models using SQLAlchemy ORM.
Single source of truth for all data.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class Job(Base):
    """Job opportunity model."""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(100), unique=True, nullable=False)
    company = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    location = Column(String(200))
    remote_option = Column(String(50))
    salary_range = Column(String(100))
    url = Column(String(500))
    description = Column(Text)
    
    # Metadata
    source = Column(String(50))  # greenhouse, lever, adzuna, etc.
    discovered_date = Column(DateTime, default=datetime.utcnow)
    relevance_score = Column(Float, default=0.0)
    
    # Application tracking
    applied = Column(Boolean, default=False)
    applied_date = Column(DateTime)
    application_method = Column(String(50))  # email, web_form, api
    
    # Email specific
    company_email = Column(String(200))
    email_verified = Column(Boolean, default=False)
    bounce_detected = Column(Boolean, default=False)
    bounce_reason = Column(String(100))
    
    # Status tracking
    status = Column(String(50), default='discovered')  # discovered, applied, responded, interview, rejected
    skip_reason = Column(Text)
    notes = Column(Text)
    
    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(company='{self.company}', position='{self.position}')>"


class Application(Base):
    """Application tracking model."""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    
    # Application details
    sent_date = Column(DateTime, default=datetime.utcnow)
    resume_version = Column(String(100))
    cover_letter = Column(Text)
    
    # Delivery tracking
    email_sent = Column(Boolean, default=False)
    email_delivered = Column(Boolean, default=False)
    delivery_status = Column(String(50))
    
    # Follow-up tracking
    follow_up_count = Column(Integer, default=0)
    last_follow_up = Column(DateTime)
    next_follow_up = Column(DateTime)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    
    def __repr__(self):
        return f"<Application(job_id={self.job_id}, sent_date='{self.sent_date}')>"


class Response(Base):
    """Response tracking model."""
    __tablename__ = 'responses'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    
    # Response details
    received_date = Column(DateTime, default=datetime.utcnow)
    response_type = Column(String(50))  # interview_request, rejection, auto_reply, other
    response_content = Column(Text)
    
    # Classification
    is_verified = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    
    # Interview specific
    interview_scheduled = Column(Boolean, default=False)
    interview_date = Column(DateTime)
    interview_type = Column(String(50))  # phone, video, onsite
    
    # Relationships
    job = relationship("Job", back_populates="responses")
    
    def __repr__(self):
        return f"<Response(job_id={self.job_id}, type='{self.response_type}')>"


class Contact(Base):
    """Contact information model."""
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    company = Column(String(200), nullable=False)
    
    # Contact details
    name = Column(String(200))
    title = Column(String(200))
    email = Column(String(200))
    linkedin_url = Column(String(500))
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    last_contacted = Column(DateTime)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Contact(name='{self.name}', company='{self.company}')>"


class EmailTemplate(Base):
    """Email template model."""
    __tablename__ = 'email_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    template_type = Column(String(50))  # application, follow_up, networking
    subject = Column(String(500))
    body = Column(Text)
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Metadata
    created_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmailTemplate(name='{self.name}', type='{self.template_type}')>"


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, database_path: str = "sqlite:///data/unified_jobs.db"):
        """Initialize database connection."""
        self.engine = create_engine(
            database_path,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()