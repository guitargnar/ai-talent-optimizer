#!/usr/bin/env python3
"""
AI Talent Optimizer - Unified CLI
Single entry point replacing 12+ separate scripts
"""

import click
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.application import ApplicationEngine
from core.job_discovery import JobDiscovery
from core.email_engine import EmailEngine
from core.resume_engine import ResumeEngine
from core.ceo_outreach_engine import CEOOutreachEngine
from utils.config import Config
from data.models import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(full_name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version='2.0.0')
def cli():
    """AI Talent Optimizer - Unified job application system"""
    pass

@cli.command()
@click.option('--limit', default=25, help='Number of applications to send')
@click.option('--priority', is_flag=True, help='Focus on priority companies only')
@click.option('--ai-focus', is_flag=True, help='Focus on AI/ML roles only')
@click.option('--verified-only', is_flag=True, help='Only apply to verified emails')
def apply(limit, priority, ai_focus, verified_only):
    """Apply to jobs (replaces 12 separate apply scripts)"""
    engine = ApplicationEngine()
    
    click.echo(f"🚀 Starting application process...")
    click.echo(f"Target: {limit} applications")
    
    if priority:
        click.echo("📌 Focusing on priority companies")
        results = engine.apply_priority_companies()
    elif ai_focus:
        click.echo("🤖 Focusing on AI/ML roles")
        results = engine.apply_top_ai_jobs()
    elif verified_only:
        click.echo("✅ Using verified emails only")
        results = engine.apply_with_verified_emails()
    else:
        click.echo("📋 Applying to all qualified jobs")
        # TODO: Implement general application
        results = {"successful": [], "failed": []}
    
    # Show results
    click.echo(f"\n📊 Results:")
    click.echo(f"✅ Successful: {len(results.get('successful', []))}")
    click.echo(f"❌ Failed: {len(results.get('failed', []))}")
    
    stats = engine.get_stats()
    click.echo(f"\n📈 Session Stats:")
    click.echo(f"Applications sent: {stats['applications_sent']}")
    click.echo(f"Emails sent: {stats['emails_sent']}")

@cli.command()
@click.option('--source', type=click.Choice(['linkedin', 'indeed', 'all']), default='all')
@click.option('--keywords', default='Principal Engineer AI ML', help='Search keywords')
@click.option('--location', default='Remote', help='Job location')
def discover(source, keywords, location):
    """Discover new job opportunities"""
    click.echo(f"🔍 Searching for: {keywords} in {location}")
    click.echo(f"Source: {source}")
    
    # TODO: Implement JobDiscovery class
    click.echo("Job discovery will be implemented in JobDiscovery class")

@cli.command()
@click.option('--company', required=True, help='Company name')
@click.option('--position', required=True, help='Position title')
def resume(company, title):
    """Generate tailored resume"""
    click.echo(f"📄 Generating resume for {position} at {company}")
    
    # TODO: Implement ResumeEngine class
    click.echo("Resume generation will be implemented in ResumeEngine class")

@cli.command()
@click.option('--check-responses', is_flag=True, help='Check for new responses')
@click.option('--send-followup', is_flag=True, help='Send follow-up emails')
def email(check_responses, send_followup):
    """Email management (responses, follow-ups)"""
    if check_responses:
        click.echo("📧 Checking for responses...")
        # TODO: Implement email checking
    
    if send_followup:
        click.echo("📤 Sending follow-up emails...")
        # TODO: Implement follow-up sending

@cli.command()
def status():
    """Show current status and statistics"""
    config = Config()
    
    click.echo("📊 AI Talent Optimizer Status")
    click.echo("=" * 50)
    
    # Personal info
    click.echo(f"\n👤 Profile:")
    click.echo(f"Name: {config.PERSONAL['name']}")
    click.echo(f"Email: {config.PERSONAL['email']}")
    click.echo(f"Phone: {config.PERSONAL['phone']}")
    click.echo(f"GitHub: {config.PERSONAL['github']}")
    
    # Database stats
    session = init_database()
    click.echo(f"\n📈 Statistics:")
    # TODO: Query actual stats from unified database
    click.echo("Applications sent: [Loading...]")
    click.echo("Responses received: [Loading...]")
    click.echo("Interview requests: [Loading...]")
    
    # System status
    click.echo(f"\n⚙️ System:")
    click.echo(f"Database: {config.DATABASE_PATH}")
    click.echo(f"Gmail OAuth: {'✅ Configured' if config.GMAIL_CREDENTIALS.exists() else '❌ Not configured'}")

@cli.command()
def migrate():
    """Migrate data from legacy databases"""
    click.echo("🔄 Starting database migration...")
    click.echo("This will consolidate data from 6 databases into 1")
    
    if click.confirm("Do you want to proceed?"):
        # TODO: Implement migration
        click.echo("Migration will be implemented in data/migrations/")
        click.echo("Will migrate from:")
        click.echo("  - job_applications.db")
        click.echo("  - principal_jobs_400k.db")
        click.echo("  - UNIFIED_AI_JOBS.db")
        click.echo("  - ceo_outreach.db")
        click.echo("  - verified_metrics.db")
        click.echo("  - your_profile.db")

@cli.command()
@click.option('--target', type=click.Choice(['ceo', 'hiring-manager', 'recruiter']), default='ceo')
@click.option('--company', help='Specific company to target')
@click.option('--research', is_flag=True, help='Research CEO contacts only')
@click.option('--send', is_flag=True, help='Send outreach emails')
@click.option('--follow-up', is_flag=True, help='Send follow-up messages')
@click.option('--report', is_flag=True, help='Generate outreach report')
@click.option('--limit', default=5, help='Number of outreach emails to send')
def outreach(target, company, research, send, follow_up, report, limit):
    """Direct outreach to CEOs/CTOs at target companies ($450K+ positions)"""
    
    if target == 'ceo':
        engine = CEOOutreachEngine()
        click.echo(f"🎯 CEO Outreach System - Targeting $450K+ Positions")
        click.echo(f"Companies: Genesis AI, Inworld AI, Adyen, Lime, Thumbtack")
        
        if research:
            click.echo(f"\n🔍 Researching CEO contacts...")
            contacts = engine.research_all_targets()
            click.echo(f"✅ Research complete: {len(contacts)} contacts discovered")
            
        elif send:
            click.echo(f"\n📧 Sending CEO outreach (limit: {limit})...")
            results = engine.send_ceo_outreach(limit=limit)
            click.echo(f"✅ Outreach sent to {len(results['sent'])} CEOs")
            click.echo(f"❌ Failed to send to {len(results['failed'])} CEOs")
            if results['sent']:
                click.echo(f"Sent to: {', '.join(results['sent'])}")
                
        elif follow_up:
            click.echo(f"\n📮 Sending follow-up messages...")
            follow_ups = engine.schedule_follow_ups()
            click.echo(f"✅ Follow-ups sent: {len(follow_ups)}")
            
        elif report:
            click.echo(f"\n📊 Generating outreach report...")
            report_text = engine.generate_outreach_report()
            click.echo(report_text)
            
        else:
            # Default: Show current status and next actions
            stats = engine.get_stats()
            click.echo(f"\n📊 Current Status:")
            click.echo(f"Target companies: {stats['target_companies']}")
            click.echo(f"Total contacts: {stats['total_contacts']}")
            click.echo(f"Contacted: {stats['contacted']}")
            click.echo(f"Total potential salary: {stats['total_potential_salary']}")
            
            click.echo(f"\n🚀 Next Actions:")
            click.echo(f"1. Research contacts: python -m cli.main outreach --research")
            click.echo(f"2. Send outreach: python -m cli.main outreach --send --limit 3")
            click.echo(f"3. Check report: python -m cli.main outreach --report")
            
    else:
        click.echo(f"🎯 Initiating {target} outreach")
        if company:
            click.echo(f"Company: {company}")
        click.echo("Other outreach types will be implemented in future versions")

@cli.command()
def dashboard():
    """Launch interactive dashboard"""
    click.echo("📊 Launching dashboard...")
    click.echo("Dashboard will provide:")
    click.echo("  - Real-time application tracking")
    click.echo("  - Response analytics")
    click.echo("  - Pipeline visualization")
    click.echo("  - Performance metrics")

if __name__ == '__main__':
    cli()