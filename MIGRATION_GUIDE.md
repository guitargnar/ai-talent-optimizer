# Migration Guide: Legacy System to v3.0 Architecture

## Overview

This guide helps you migrate from the legacy multi-database, multi-script system to the new unified architecture.

## Pre-Migration Checklist

- [ ] Python 3.8+ installed
- [ ] Access to legacy databases
- [ ] Gmail credentials ready
- [ ] 30 minutes for migration

## Migration Steps

### Step 1: Backup Existing Data

**Critical**: Always backup before migrating!

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup all databases
cp *.db backups/$(date +%Y%m%d)/

# Backup legacy scripts (optional)
tar -czf backups/legacy_scripts_$(date +%Y%m%d).tar.gz *.py
```

### Step 2: Install New System

```bash
# Ensure you're in the project directory
cd /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer

# Install required packages
pip install sqlalchemy click python-dotenv

# Create data directory
mkdir -p data
```

### Step 3: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit with your credentials
nano .env
```

Required fields in `.env`:
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
ADZUNA_APP_ID=your_id (optional)
ADZUNA_APP_KEY=your_key (optional)
```

### Step 4: Run Migration

#### Option A: Quick Migration (Recommended)

```bash
# Fast migration from main database
python quick_migrate.py
```

This will:
- Import jobs from UNIFIED_AI_JOBS.db
- Create new unified database
- Show migration statistics

#### Option B: Full Migration

```bash
# Comprehensive migration from all databases
python migrations/migrate_to_unified.py
```

This attempts to merge all legacy databases but may encounter issues with schema differences.

### Step 5: Verify Migration

```bash
# Check system status
python main.py status

# View metrics
python main.py metrics

# Test with dry run
python main.py apply --count 1 --dry-run
```

### Step 6: Archive Legacy Files

Once verified, move old files to archive:

```bash
# Already done automatically
# Check legacy_archive/ directory
ls -la legacy_archive/
```

## Data Mapping

### Legacy Database → New Database

| Old Database | Old Table | New Table | Notes |
|-------------|-----------|-----------|-------|
| UNIFIED_AI_JOBS.db | job_discoveries | jobs | Main job data |
| applications_sent.db | applications | applications | Application history |
| email_tracking.db | emails | applications | Merged |
| bounce_detection.db | bounces | jobs.bounce_detected | Integrated |
| response_tracking.db | responses | responses | Response tracking |

### Legacy Scripts → New Commands

| Old Script | New Command | Description |
|------------|-------------|-------------|
| apply_top_ai_jobs.py | `python main.py apply` | Send applications |
| automated_apply.py | `python main.py apply --count N` | Batch applications |
| check_automation_status.py | `python main.py status` | System status |
| accurate_response_checker.py | `python main.py check-responses` | Check responses |
| send_followup_email.py | `python main.py follow-up ID` | Send follow-up |
| true_metrics_dashboard.py | `python main.py metrics` | View metrics |

## Common Issues & Solutions

### Issue: ModuleNotFoundError

```bash
# Set Python path
export PYTHONPATH=$PWD:$PYTHONPATH

# Or install as package
pip install -e .
```

### Issue: Database Locked

```bash
# Close other connections
fuser data/unified_jobs.db
kill -9 [PID]

# Or restart
python main.py clean
```

### Issue: Missing Credentials

```bash
# Check .env file
cat .env | grep EMAIL

# Get Gmail app password:
# 1. Go to Google Account settings
# 2. Security → 2-Step Verification
# 3. App passwords → Generate
```

### Issue: Import Errors from Legacy Code

```bash
# Legacy files are archived, not imported
# Use new commands instead:
python main.py --help
```

## Post-Migration

### Recommended Next Steps

1. **Test core functions**:
   ```bash
   python main.py apply --dry-run
   python main.py status
   ```

2. **Review migrated data**:
   ```bash
   sqlite3 data/unified_jobs.db
   .tables
   SELECT COUNT(*) FROM jobs;
   SELECT COUNT(*) FROM jobs WHERE applied = 1;
   .quit
   ```

3. **Update any automation**:
   - Replace cron jobs with new commands
   - Update shell aliases
   - Review custom scripts

4. **Clean up** (after 1 week):
   ```bash
   # Once confident, remove legacy archive
   rm -rf legacy_archive/
   ```

## Rollback Plan

If you need to revert:

```bash
# Restore from backup
cp backups/[date]/*.db .

# Use legacy scripts from archive
cp legacy_archive/*.py .
```

## Benefits of Migration

### Immediate Benefits
- ✅ Single command interface
- ✅ 85% less code to maintain
- ✅ Unified database queries
- ✅ Secure credential management
- ✅ No more import errors

### Long-term Benefits
- ✅ Easier debugging
- ✅ Faster execution
- ✅ Better testing
- ✅ Professional architecture
- ✅ Ready for scaling

## Support

For issues or questions:
- Check [ARCHITECTURE_REFACTOR.md](ARCHITECTURE_REFACTOR.md)
- Review [SYSTEM_TEST_REPORT.md](SYSTEM_TEST_REPORT.md)
- See main [README.md](README.md)

---

*Migration typically takes 5-10 minutes. The new system is significantly faster and more reliable than the legacy version.*