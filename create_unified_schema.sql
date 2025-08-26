-- ============================================================================
-- UNIFIED DATABASE SCHEMA
-- AI Talent Optimizer Platform v3.0
-- 
-- Purpose: Create a single, consolidated database schema to replace the
--          fragmented 19-database system
-- 
-- Generated: 2025-08-26
-- ============================================================================

-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS system_log;
DROP TABLE IF EXISTS metrics;
DROP TABLE IF EXISTS emails;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS profile;

-- ============================================================================
-- 1. COMPANIES TABLE
-- Purpose: Company intelligence and research data
-- Note: Created first as it's referenced by other tables
-- ============================================================================
CREATE TABLE companies (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Company Identification
    name TEXT UNIQUE NOT NULL,
    legal_name TEXT,
    ticker TEXT,
    
    -- Company Details
    industry TEXT,
    sub_industry TEXT,
    size_range TEXT,  -- '1-10', '11-50', '51-200', '201-500', '501-1000', '1000-5000', '5000+'
    employee_count INTEGER,
    founded_year INTEGER,
    
    -- Location
    headquarters_city TEXT,
    headquarters_state TEXT,
    headquarters_country TEXT,
    
    -- Digital Presence
    website TEXT,
    careers_page TEXT,
    linkedin_url TEXT,
    glassdoor_url TEXT,
    
    -- Email Patterns
    email_domain TEXT,
    email_pattern TEXT,  -- '{first}.{last}', '{f}{last}', etc.
    
    -- Company Culture
    culture_notes TEXT,
    tech_stack TEXT,  -- JSON array
    interview_process TEXT,
    
    -- Financial
    funding_stage TEXT,
    total_funding INTEGER,
    valuation INTEGER,
    revenue_range TEXT,
    
    -- Scoring
    priority_score REAL DEFAULT 0.0,
    culture_fit_score REAL DEFAULT 0.0,
    growth_score REAL DEFAULT 0.0,
    
    -- Research
    research_notes TEXT,
    recent_news TEXT,
    key_products TEXT,
    competitors TEXT,
    
    -- Application Strategy
    preferred_apply_method TEXT,
    application_tips TEXT,
    avoid_reasons TEXT,
    
    -- Metadata
    last_researched TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for companies
CREATE INDEX idx_companies_priority ON companies(priority_score DESC);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_name ON companies(name);

-- ============================================================================
-- 2. JOBS TABLE
-- Purpose: Centralized repository of all job opportunities from all sources
-- ============================================================================
CREATE TABLE jobs (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Unique Identifiers
    job_id TEXT UNIQUE NOT NULL,  -- External ID from source
    source TEXT NOT NULL,          -- 'linkedin', 'indeed', 'company_site', etc.
    
    -- Core Job Information
    company TEXT NOT NULL,
    company_id INTEGER,
    title TEXT NOT NULL,
    department TEXT,
    level TEXT,  -- 'entry', 'mid', 'senior', 'staff', 'principal', 'director'
    
    -- Location
    location TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'USA',
    remote_type TEXT,  -- 'remote', 'hybrid', 'onsite'
    
    -- Compensation
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency TEXT DEFAULT 'USD',
    equity_offered BOOLEAN DEFAULT 0,
    
    -- Job Details
    description TEXT,
    requirements TEXT,
    responsibilities TEXT,
    benefits TEXT,
    tech_stack TEXT,  -- JSON array of technologies
    
    -- URLs and References
    url TEXT,
    apply_url TEXT,
    
    -- Scoring and Priority
    relevance_score REAL DEFAULT 0.0,
    priority_score REAL DEFAULT 0.0,
    ai_match_score REAL DEFAULT 0.0,
    
    -- Categorization
    is_ai_ml_focused BOOLEAN DEFAULT 0,
    is_healthcare BOOLEAN DEFAULT 0,
    is_principal_plus BOOLEAN DEFAULT 0,
    requires_clearance BOOLEAN DEFAULT 0,
    
    -- Status Tracking
    status TEXT DEFAULT 'new',  -- 'new', 'reviewing', 'applied', 'rejected', 'expired'
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_date TIMESTAMP,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Indexes for jobs
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_priority ON jobs(priority_score DESC);
CREATE INDEX idx_jobs_discovered ON jobs(discovered_date DESC);
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_title ON jobs(title);

-- ============================================================================
-- 3. APPLICATIONS TABLE
-- Purpose: Track all job applications and their lifecycle
-- ============================================================================
CREATE TABLE applications (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    job_id INTEGER NOT NULL,
    company_id INTEGER,
    
    -- Application Details
    company_name TEXT NOT NULL,  -- Denormalized for quick access
    position TEXT NOT NULL,       -- Denormalized for quick access
    
    -- Application Method
    method TEXT NOT NULL,  -- 'email', 'linkedin', 'portal', 'referral'
    email_to TEXT,
    portal_url TEXT,
    
    -- Content Used
    resume_version TEXT NOT NULL,
    cover_letter_version TEXT,
    email_subject TEXT,
    email_body TEXT,
    
    -- Tracking
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    followup_date_1 TIMESTAMP,
    followup_date_2 TIMESTAMP,
    
    -- Status
    status TEXT DEFAULT 'pending',  -- 'pending', 'sent', 'viewed', 'responded', 'interview', 'offer', 'rejected'
    response_received BOOLEAN DEFAULT 0,
    response_date TIMESTAMP,
    
    -- Interview Process
    interview_scheduled BOOLEAN DEFAULT 0,
    interview_round INTEGER DEFAULT 0,
    interview_dates TEXT,  -- JSON array
    interview_notes TEXT,
    
    -- Outcome
    offer_received BOOLEAN DEFAULT 0,
    offer_amount INTEGER,
    rejection_reason TEXT,
    
    -- Quality Metrics
    personalization_score REAL DEFAULT 0.0,
    ats_score REAL DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Indexes for applications
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_company ON applications(company_name);
CREATE INDEX idx_applications_applied_date ON applications(applied_date DESC);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_response ON applications(response_received);

-- ============================================================================
-- 4. CONTACTS TABLE
-- Purpose: People network - CEOs, hiring managers, recruiters, referrals
-- ============================================================================
CREATE TABLE contacts (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    company_id INTEGER,
    
    -- Contact Information
    full_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    title TEXT,
    department TEXT,
    
    -- Contact Methods
    email TEXT,
    email_verified BOOLEAN DEFAULT 0,
    linkedin_url TEXT,
    phone TEXT,
    twitter TEXT,
    
    -- Categorization
    contact_type TEXT,  -- 'ceo', 'cto', 'hiring_manager', 'recruiter', 'employee', 'referral'
    seniority_level TEXT,  -- 'c_level', 'vp', 'director', 'manager', 'senior', 'mid'
    
    -- Relationship
    relationship_strength INTEGER DEFAULT 0,  -- 0-10 scale
    how_met TEXT,
    mutual_connections INTEGER,
    
    -- Outreach Tracking
    contacted BOOLEAN DEFAULT 0,
    contacted_date TIMESTAMP,
    contact_method TEXT,
    message_sent TEXT,
    
    -- Response Tracking
    response_received BOOLEAN DEFAULT 0,
    response_date TIMESTAMP,
    response_content TEXT,
    response_sentiment TEXT,  -- 'positive', 'neutral', 'negative'
    
    -- Meeting/Call Tracking
    meeting_scheduled BOOLEAN DEFAULT 0,
    meeting_date TIMESTAMP,
    meeting_notes TEXT,
    
    -- Scoring
    influence_score REAL DEFAULT 0.0,
    responsiveness_score REAL DEFAULT 0.0,
    priority_score REAL DEFAULT 0.0,
    
    -- Notes
    bio TEXT,
    interests TEXT,
    notes TEXT,
    
    -- Metadata
    source TEXT,  -- Where/how we found them
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Indexes for contacts
CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_contacts_type ON contacts(contact_type);
CREATE INDEX idx_contacts_contacted ON contacts(contacted);
CREATE INDEX idx_contacts_name ON contacts(full_name);
CREATE INDEX idx_contacts_email ON contacts(email);

-- ============================================================================
-- 5. EMAILS TABLE
-- Purpose: Email communications and responses
-- ============================================================================
CREATE TABLE emails (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    application_id INTEGER,
    contact_id INTEGER,
    
    -- Email Identification
    message_id TEXT UNIQUE,
    thread_id TEXT,
    
    -- Email Details
    direction TEXT NOT NULL,  -- 'sent', 'received'
    from_email TEXT,
    to_email TEXT,
    cc_emails TEXT,
    bcc_emails TEXT,
    
    -- Content
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    
    -- Categorization
    email_type TEXT,  -- 'application', 'followup', 'response', 'rejection', 'interview', 'offer'
    is_automated BOOLEAN DEFAULT 0,
    
    -- Status
    status TEXT,  -- 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed'
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    
    -- Timestamps
    sent_date TIMESTAMP,
    received_date TIMESTAMP,
    opened_date TIMESTAMP,
    
    -- Analysis
    sentiment TEXT,
    action_required BOOLEAN DEFAULT 0,
    action_taken TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

-- Indexes for emails
CREATE INDEX idx_emails_thread ON emails(thread_id);
CREATE INDEX idx_emails_type ON emails(email_type);
CREATE INDEX idx_emails_received ON emails(received_date DESC);
CREATE INDEX idx_emails_application ON emails(application_id);
CREATE INDEX idx_emails_direction ON emails(direction);

-- ============================================================================
-- 6. METRICS TABLE
-- Purpose: Performance tracking and analytics
-- ============================================================================
CREATE TABLE metrics (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Metric Identification
    metric_name TEXT NOT NULL,
    metric_category TEXT NOT NULL,  -- 'application', 'response', 'interview', 'system', 'quality'
    
    -- Values
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    
    -- Time Period
    date DATE NOT NULL,
    week_number INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    
    -- Context
    context TEXT,  -- JSON object with additional context
    
    -- Verification
    is_verified BOOLEAN DEFAULT 0,
    verification_method TEXT,
    verified_date TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for metrics
CREATE INDEX idx_metrics_name_date ON metrics(metric_name, date DESC);
CREATE INDEX idx_metrics_category ON metrics(metric_category);
CREATE INDEX idx_metrics_date ON metrics(date DESC);

-- ============================================================================
-- 7. PROFILE TABLE
-- Purpose: User profile and configuration (single record)
-- ============================================================================
CREATE TABLE profile (
    -- Primary Key (constrained to single record)
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    
    -- Personal Information
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    
    -- Online Presence
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    personal_website TEXT,
    
    -- Location
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'USA',
    timezone TEXT DEFAULT 'America/New_York',
    willing_to_relocate BOOLEAN DEFAULT 1,
    preferred_locations TEXT,  -- JSON array
    
    -- Professional Identity
    current_title TEXT,
    years_experience INTEGER,
    career_level TEXT,  -- 'junior', 'mid', 'senior', 'staff', 'principal', 'director'
    
    -- Target Preferences
    target_roles TEXT,  -- JSON array
    target_companies TEXT,  -- JSON array
    target_industries TEXT,  -- JSON array
    target_salary_min INTEGER,
    target_salary_max INTEGER,
    
    -- Skills
    primary_skills TEXT,  -- JSON array
    secondary_skills TEXT,  -- JSON array
    certifications TEXT,  -- JSON array
    
    -- Resume Management
    resume_versions TEXT,  -- JSON object with version names and paths
    cover_letter_templates TEXT,  -- JSON object
    default_resume_version TEXT,
    
    -- Application Preferences
    max_applications_per_day INTEGER DEFAULT 10,
    preferred_apply_method TEXT,
    auto_apply_enabled BOOLEAN DEFAULT 0,
    
    -- Email Configuration
    smtp_configured BOOLEAN DEFAULT 0,
    gmail_oauth_configured BOOLEAN DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 8. SYSTEM_LOG TABLE
-- Purpose: Audit trail and system events
-- ============================================================================
CREATE TABLE system_log (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Event Details
    event_type TEXT NOT NULL,  -- 'application_sent', 'email_received', 'job_discovered', etc.
    event_category TEXT NOT NULL,  -- 'job', 'application', 'email', 'system'
    event_description TEXT,
    
    -- References
    entity_type TEXT,  -- 'job', 'application', 'contact', etc.
    entity_id INTEGER,
    
    -- Context
    user_action BOOLEAN DEFAULT 0,
    automation_triggered BOOLEAN DEFAULT 0,
    
    -- Result
    success BOOLEAN DEFAULT 1,
    error_message TEXT,
    
    -- Metadata
    session_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for system_log
CREATE INDEX idx_system_log_type ON system_log(event_type);
CREATE INDEX idx_system_log_created ON system_log(created_at DESC);
CREATE INDEX idx_system_log_category ON system_log(event_category);
CREATE INDEX idx_system_log_entity ON system_log(entity_type, entity_id);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Trigger for companies table
CREATE TRIGGER update_companies_timestamp 
AFTER UPDATE ON companies
BEGIN
    UPDATE companies SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger for jobs table
CREATE TRIGGER update_jobs_timestamp 
AFTER UPDATE ON jobs
BEGIN
    UPDATE jobs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger for applications table
CREATE TRIGGER update_applications_timestamp 
AFTER UPDATE ON applications
BEGIN
    UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger for contacts table
CREATE TRIGGER update_contacts_timestamp 
AFTER UPDATE ON contacts
BEGIN
    UPDATE contacts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger for profile table
CREATE TRIGGER update_profile_timestamp 
AFTER UPDATE ON profile
BEGIN
    UPDATE profile SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active job opportunities
CREATE VIEW active_jobs AS
SELECT 
    j.*,
    c.name as company_name,
    c.industry,
    c.email_domain
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.id
WHERE j.status IN ('new', 'reviewing')
AND (j.expires_date IS NULL OR j.expires_date > CURRENT_TIMESTAMP);

-- View: Recent applications with responses
CREATE VIEW application_responses AS
SELECT 
    a.*,
    j.title as job_title,
    j.company as job_company,
    e.received_date as last_response_date,
    e.email_type as response_type
FROM applications a
JOIN jobs j ON a.job_id = j.id
LEFT JOIN emails e ON a.id = e.application_id AND e.direction = 'received'
WHERE a.response_received = 1;

-- View: Contact network summary
CREATE VIEW contact_network AS
SELECT 
    c.*,
    comp.name as company_name,
    comp.industry,
    (SELECT COUNT(*) FROM emails WHERE contact_id = c.id) as email_count
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id;

-- ============================================================================
-- INITIAL DATA INSERTION
-- ============================================================================

-- Insert default profile record
INSERT OR IGNORE INTO profile (
    full_name,
    email,
    phone,
    linkedin_url,
    github_url,
    city,
    state,
    current_title,
    years_experience,
    career_level,
    target_salary_min,
    target_salary_max
) VALUES (
    'Matthew Scott',
    'matthewdscott7@gmail.com',
    '(502) 345-0525',
    'linkedin.com/in/mscott77',
    'github.com/guitargnar',
    'Louisville',
    'KY',
    'Senior AI/ML Engineer',
    10,
    'senior',
    150000,
    400000
);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version, description) 
VALUES (1, 'Initial unified schema creation - 8 core tables');

-- ============================================================================
-- END OF SCHEMA CREATION
-- ============================================================================