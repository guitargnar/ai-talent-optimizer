# 📚 AI Talent Optimizer - API Reference

Complete API documentation for all components of the AI Talent Optimizer system.

## Table of Contents
1. [Discovery Dashboard](#discovery-dashboard)
2. [AI Recruiter Analyzer](#ai-recruiter-analyzer)
3. [Profile Optimizer](#profile-optimizer)
4. [Signal Booster](#signal-booster)
5. [ATS/AI Resume Generator](#atsai-resume-generator)
6. [Email Application Tracker](#email-application-tracker)
7. [Visibility Amplifier](#visibility-amplifier)
8. [Gmail OAuth Integration](#gmail-oauth-integration)

---

## Discovery Dashboard

### Class: `DiscoveryDashboard`
Unified monitoring and control center for all job search activities.

#### Methods

##### `__init__(self)`
Initialize all subsystems and connections.

##### `generate_dashboard(self) -> Dict`
Generate complete dashboard data.

**Returns:**
```python
{
    'generated_at': str,  # ISO timestamp
    'executive_summary': Dict,
    'discovery_metrics': Dict,
    'application_metrics': Dict,
    'response_metrics': Dict,
    'signal_metrics': Dict,
    'daily_actions': List[Dict],
    'insights': List[str]
}
```

##### `display_dashboard(self, dashboard_data: Dict)`
Display dashboard in terminal with formatted output.

##### `export_dashboard(self, dashboard_data: Dict, format: str = 'json') -> str`
Export dashboard data to file.

**Parameters:**
- `format`: 'json' or 'html'

**Returns:** Filename of exported dashboard

##### `start_live_monitoring(self)`
Start continuous dashboard monitoring (updates every 5 minutes).

---

## AI Recruiter Analyzer

### Class: `AIRecruiterAnalyzer`
Analyzes AI recruitment platforms and provides optimization strategies.

#### Methods

##### `analyze_platform(self, platform_name: str) -> Dict`
Analyze specific recruitment platform.

**Parameters:**
- `platform_name`: One of ['linkedin_recruiter', 'github_hiring', 'seekout', 'hirevue', 'workday']

**Returns:**
```python
{
    'platform': str,
    'optimization_score': float,  # 0-1
    'missing_elements': List[str],
    'recommendations': List[str],
    'keyword_analysis': Dict
}
```

##### `generate_visibility_report(self) -> Dict`
Generate comprehensive visibility analysis across all platforms.

##### `calculate_overall_visibility_score(self, profile_data: Dict) -> float`
Calculate aggregate visibility score (0-100).

---

## Profile Optimizer

### Class: `ProfileOptimizer`
Optimizes online profiles for maximum AI visibility.

#### Properties
- `keywords`: Dict of keyword categories
- `profiles`: Dict of profile optimization targets

#### Methods

##### `scan_profile(self, platform: str, profile_data: Dict) -> Dict`
Analyze current profile and identify improvements.

**Returns:**
```python
{
    'current_score': float,
    'missing_keywords': List[str],
    'keyword_density': Dict,
    'recommendations': List[str]
}
```

##### `generate_optimized_content(self, platform: str) -> str`
Generate platform-specific optimized content.

##### `create_content_calendar(self) -> Dict`
Create 30-day content publishing calendar.

---

## Signal Booster

### Class: `SignalBooster`
Generates and tracks high-value activities for AI recruiter visibility.

### Dataclass: `SignalActivity`
```python
@dataclass
class SignalActivity:
    activity_type: str
    platform: str
    action: str
    impact_score: float  # 0-1
    time_required: int   # minutes
    frequency: str       # daily, weekly, monthly
    keywords: List[str]
    expected_outcome: str
```

#### Methods

##### `generate_daily_plan(self) -> Dict`
Generate optimized daily activity plan.

**Returns:**
```python
{
    'date': str,
    'day': str,
    'total_time': int,  # minutes
    'expected_impact': float,
    'activities': List[Dict],
    'schedule': List[Dict]
}
```

##### `generate_weekly_strategy(self) -> Dict`
Generate weekly signal boosting strategy.

##### `track_activity_completion(self, activity_id: str, notes: str = '') -> Dict`
Track completion of signal activities.

##### `generate_impact_report(self) -> Dict`
Generate report on signal boosting effectiveness.

---

## ATS/AI Resume Generator

### Class: `ATSAIOptimizer`
Creates multiple resume versions optimized for different systems.

### Dataclass: `ResumeVersion`
```python
@dataclass
class ResumeVersion:
    name: str
    focus: str
    keywords: List[str]
    sections: Dict[str, str]
    invisible_keywords: str
    ats_score: float
```

#### Methods

##### `generate_master_version(self) -> ResumeVersion`
Generate comprehensive resume with all keywords.

##### `generate_linkedin_version(self) -> ResumeVersion`
Generate LinkedIn-optimized resume.

##### `generate_technical_version(self) -> ResumeVersion`
Generate technical deep-dive resume.

##### `generate_executive_version(self) -> ResumeVersion`
Generate leadership-focused resume.

##### `export_resumes(self)`
Export all resume versions to files.

---

## Email Application Tracker

### Class: `EmailApplicationTracker`
Tracks all email-based job applications.

#### Methods

##### `log_email_application(self, application_data: Dict)`
Log new email application.

**Parameters:**
```python
{
    'to_email': str,
    'subject': str,
    'company': str,
    'position': str,
    'sent_date': str,  # YYYY-MM-DD
    'personalized': str,  # yes/no
    'salary_range': str,  # e.g., "250000-350000"
    # ... (17 additional optional fields)
}
```

##### `search_email_applications(self, search_term: str = '') -> List[Dict]`
Search applications by any field.

##### `update_application_status(self, email_id: str, updates: Dict)`
Update existing application record.

##### `get_response_metrics(self) -> Dict`
Calculate response rates and metrics.

##### `generate_email_report(self) -> Dict`
Generate comprehensive email application report.

---

## Visibility Amplifier

### Class: `VisibilityAmplifier`
Generates SEO-optimized content for maximum discovery.

### Dataclass: `SEOContent`
```python
@dataclass
class SEOContent:
    title: str
    meta_description: str
    keywords: List[str]
    content: str
    schema_markup: Dict
    platform_tags: List[str]
    optimal_posting_time: str
```

#### Methods

##### `generate_seo_content(self, content_type: str, topic: str) -> SEOContent`
Generate platform-optimized content.

**Parameters:**
- `content_type`: One of ['article', 'case_study', 'technical_post', 'achievement_summary']
- `topic`: Content topic/focus

##### `create_schema_markup(self, content_type: str) -> Dict`
Generate structured data markup.

##### `generate_platform_strategy(self, platform: str) -> Dict`
Create platform-specific visibility strategy.

---

## Gmail OAuth Integration

### Class: `GmailOAuthIntegration`
Connects Gmail monitoring with application tracking.

#### Properties
- `monitored_companies`: List of companies being monitored
- `gmail_path`: Path to Gmail OAuth directory

#### Methods

##### `sync_gmail_responses(self) -> List[str]`
Sync Gmail responses with tracker.

**Returns:** List of processed message IDs

##### `_classify_response(self, reply: Dict) -> str`
Classify email response type.

**Returns:** One of:
- 'interview_request'
- 'next_steps'
- 'personal_reply'
- 'auto_acknowledgment'
- 'rejection'
- 'auto_response'

##### `generate_unified_report(self) -> Dict`
Generate report combining all tracking systems.

##### `create_monitoring_script(self)`
Create unified monitoring script file.

---

## Common Patterns

### Error Handling
All methods follow this pattern:
```python
try:
    # Operation
    return result
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return default_value
```

### File I/O
All file operations use:
```python
os.makedirs(os.path.dirname(filepath), exist_ok=True)
with open(filepath, 'w') as f:
    # Write operation
```

### Data Persistence
- CSV files for tabular data
- JSON files for structured data
- Pickle files for OAuth tokens

---

## Usage Examples

### Complete Daily Workflow
```python
from discovery_dashboard import DiscoveryDashboard
from signal_booster import SignalBooster
from email_application_tracker import EmailApplicationTracker

# Morning routine
dashboard = DiscoveryDashboard()
data = dashboard.generate_dashboard()
dashboard.display_dashboard(data)

# Get activities
booster = SignalBooster()
daily_plan = booster.generate_daily_plan()

# Track applications
tracker = EmailApplicationTracker()
tracker.log_email_application({
    'company': 'OpenAI',
    'position': 'Research Engineer',
    'sent_date': '2025-08-05'
})

# Export summary
dashboard.export_dashboard(data, 'html')
```

### Custom Analysis
```python
from ai_recruiter_analyzer import AIRecruiterAnalyzer
from profile_optimizer import ProfileOptimizer

# Analyze specific platform
analyzer = AIRecruiterAnalyzer()
linkedin_analysis = analyzer.analyze_platform('linkedin_recruiter')

# Optimize profile
optimizer = ProfileOptimizer()
profile_data = {'current_headline': 'AI Engineer'}
optimization = optimizer.scan_profile('linkedin', profile_data)
```

---

*This API reference covers all public methods and classes in the AI Talent Optimizer system. For implementation details, see the source code.*