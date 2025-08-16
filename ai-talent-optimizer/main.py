#!/usr/bin/env python3
"""
AI Talent Optimizer - Main CLI Interface
Professional job application automation system.
"""

import click
import logging
from pathlib import Path
from typing import Optional
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.application import ApplicationService
from src.models.database import DatabaseManager
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format,
    handlers=[
        logging.FileHandler(settings.logging.file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='2.0.0')
def cli():
    """AI Talent Optimizer - Professional job application automation."""
    # Validate configuration on startup
    errors = settings.validate()
    if errors:
        click.echo(click.style("⚠️  Configuration Issues:", fg='yellow'))
        for error in errors:
            click.echo(f"  • {error}")
        click.echo("\nRun 'talent-optimizer setup' to configure")


@cli.command()
def setup():
    """Interactive setup wizard."""
    click.echo("🔧 AI Talent Optimizer Setup")
    click.echo("=" * 50)
    
    # Check for .env file
    env_path = Path('.env')
    if not env_path.exists():
        click.echo("Creating .env file from template...")
        
        # Copy template
        template_path = Path('.env.template')
        if template_path.exists():
            env_path.write_text(template_path.read_text())
            click.echo("✅ Created .env file")
        else:
            click.echo("❌ .env.template not found")
            return
    
    # Prompt for required values
    click.echo("\nPlease configure the following:")
    
    email = click.prompt("Gmail address", default=settings.email.address or "")
    app_password = click.prompt("Gmail app password", hide_input=True, default="")
    
    # Update .env file
    env_content = env_path.read_text()
    env_content = env_content.replace('your_email@gmail.com', email)
    env_content = env_content.replace('your_app_specific_password', app_password)
    env_path.write_text(env_content)
    
    click.echo("\n✅ Configuration saved to .env")
    click.echo("Run 'talent-optimizer status' to verify")


@cli.command()
def status():
    """Check system status and configuration."""
    click.echo("📊 System Status")
    click.echo("=" * 50)
    
    # Configuration status
    errors = settings.validate()
    if errors:
        click.echo(click.style("❌ Configuration Issues:", fg='red'))
        for error in errors:
            click.echo(f"  • {error}")
    else:
        click.echo(click.style("✅ Configuration Valid", fg='green'))
    
    # Database status
    try:
        db = DatabaseManager()
        session = db.get_session()
        
        # Get counts
        from src.models.database import Job, Application, Response
        
        total_jobs = session.query(Job).count()
        applied = session.query(Job).filter_by(applied=True).count()
        responses = session.query(Response).count()
        
        click.echo(f"\n📈 Database Statistics:")
        click.echo(f"  • Total jobs: {total_jobs}")
        click.echo(f"  • Applications sent: {applied}")
        click.echo(f"  • Responses received: {responses}")
        
        session.close()
        
    except Exception as e:
        click.echo(click.style(f"❌ Database Error: {e}", fg='red'))
    
    # Email status
    if settings.email.is_configured:
        click.echo(f"\n📧 Email Configuration:")
        click.echo(f"  • Address: {settings.email.address}")
        click.echo(f"  • SMTP: {settings.email.smtp_server}:{settings.email.smtp_port}")
    else:
        click.echo(click.style("\n❌ Email not configured", fg='red'))


@cli.command()
@click.option('--count', '-c', default=10, help='Number of applications to send')
@click.option('--min-score', '-s', default=0.65, help='Minimum relevance score')
@click.option('--dry-run', is_flag=True, help='Preview without sending')
def apply(count: int, min_score: float, dry_run: bool):
    """Send job applications in batch."""
    click.echo(f"📤 Sending {count} Applications")
    click.echo("=" * 50)
    
    if dry_run:
        click.echo(click.style("DRY RUN MODE - No emails will be sent", fg='yellow'))
    
    # Initialize service
    app_service = ApplicationService()
    
    # Get eligible jobs
    db = DatabaseManager()
    session = db.get_session()
    
    from src.models.database import Job
    
    jobs = session.query(Job).filter(
        Job.applied == False,
        Job.relevance_score >= min_score,
        Job.bounce_detected == False
    ).order_by(Job.relevance_score.desc()).limit(count).all()
    
    click.echo(f"\nFound {len(jobs)} eligible jobs:\n")
    
    for i, job in enumerate(jobs, 1):
        click.echo(f"{i}. {job.company} - {job.position}")
        click.echo(f"   Score: {job.relevance_score:.2f}, Email: {job.company_email or 'N/A'}")
    
    if not jobs:
        click.echo("\nNo eligible jobs found. Try:")
        click.echo("  • Lowering minimum score with -s 0.5")
        click.echo("  • Adding more jobs with 'talent-optimizer scrape'")
        return
    
    if dry_run:
        click.echo("\nDry run complete. Remove --dry-run to send applications.")
        return
    
    # Confirm before sending
    if not click.confirm("\nProceed with sending applications?"):
        click.echo("Cancelled")
        return
    
    # Send applications
    click.echo("\nSending applications...")
    results = app_service.batch_apply(count, min_score)
    
    # Show results
    click.echo("\n📊 Results:")
    click.echo(f"  ✅ Success: {results['success']}")
    click.echo(f"  ❌ Failed: {results['failed']}")
    
    if results['errors']:
        click.echo("\nErrors:")
        for error in results['errors'][:5]:
            click.echo(f"  • {error}")
    
    session.close()


@cli.command()
def metrics():
    """Show application metrics and statistics."""
    click.echo("📊 Application Metrics")
    click.echo("=" * 50)
    
    app_service = ApplicationService()
    stats = app_service.get_application_stats()
    
    click.echo(f"\n📈 Overall Statistics:")
    click.echo(f"  • Total jobs in database: {stats['total_jobs']}")
    click.echo(f"  • Applications sent: {stats['applications_sent']}")
    click.echo(f"  • Responses received: {stats['responses_received']}")
    click.echo(f"  • Interviews scheduled: {stats['interviews_scheduled']}")
    
    click.echo(f"\n📊 Success Rates:")
    click.echo(f"  • Response rate: {stats['response_rate']}%")
    click.echo(f"  • Interview rate: {stats['interview_rate']}%")
    
    click.echo(f"\n📅 Daily Limits:")
    click.echo(f"  • Sent today: {stats['daily_sent']}")
    click.echo(f"  • Daily limit: {stats['daily_limit']}")
    click.echo(f"  • Remaining: {stats['daily_limit'] - stats['daily_sent']}")


@cli.command()
@click.argument('job_id', type=int)
def follow_up(job_id: int):
    """Send follow-up email for a job application."""
    click.echo(f"📮 Sending Follow-up for Job {job_id}")
    click.echo("=" * 50)
    
    app_service = ApplicationService()
    success, message = app_service.send_follow_up(job_id)
    
    if success:
        click.echo(click.style(f"✅ {message}", fg='green'))
    else:
        click.echo(click.style(f"❌ {message}", fg='red'))


@cli.command()
def clean():
    """Clean up and optimize the system."""
    click.echo("🧹 System Cleanup")
    click.echo("=" * 50)
    
    # Archive old logs
    log_dir = Path('logs')
    if log_dir.exists():
        old_logs = list(log_dir.glob('*.log.*'))
        if old_logs:
            click.echo(f"Archiving {len(old_logs)} old log files...")
            # TODO: Implement log archiving
    
    # Vacuum database
    click.echo("Optimizing database...")
    db = DatabaseManager()
    db.engine.execute("VACUUM")
    
    # Clean temp files
    temp_files = list(Path('.').glob('*.tmp')) + list(Path('.').glob('*.backup'))
    if temp_files:
        click.echo(f"Removing {len(temp_files)} temporary files...")
        for f in temp_files:
            f.unlink()
    
    click.echo("\n✅ Cleanup complete")


if __name__ == '__main__':
    cli()