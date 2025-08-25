# 🎯 Job Application Automation Dashboard

## Quick Commands

### 🇪🇺 European Jobs (10 positions ready)
```bash
# View and apply to European positions
python3 apply_to_european_jobs.py

# Fetch more European jobs
python3 european_job_fetcher.py

# Quick fetch with sample data
python3 fetch_european_jobs_now.py
```

### 🔗 LinkedIn Easy Apply
```bash
# Interactive LinkedIn application
python3 quick_linkedin_apply.py

# Process job URLs from file
python3 linkedin_job_processor.py

# Single job URL
python3 linkedin_job_processor.py --url https://linkedin.com/jobs/view/123
```

### 📊 View Progress
```bash
# Check master tracker
grep "TODO" MASTER_TRACKER_400K.csv | grep "HIGHEST" | wc -l
# Shows number of highest priority TODOs

# View European positions
sqlite3 data/european_jobs.db "SELECT company, position, salary_range FROM european_jobs;"

# List tailored resumes
ls -la resumes/european/
```

## Current Status

### European Opportunities (Visa Sponsored)
| Company | Location | Salary | Status |
|---------|----------|--------|--------|
| DeepMind | London, UK | £120K-£180K | ✅ Resume Ready |
| Spotify | Stockholm | SEK 900K-1.3M | ✅ Resume Ready |
| Booking.com | Amsterdam | €110K-€160K | ✅ Resume Ready |
| Revolut | London, UK | £110K-£170K | ✅ Resume Ready |
| Adyen | Amsterdam | €120K-€170K | ✅ Resume Ready |
| Datadog | Paris | €100K-€150K | ✅ Resume Ready |
| Zalando | Berlin | €95K-€140K | ✅ Resume Ready |
| Klarna | Stockholm | SEK 750K-1.1M | ✅ Resume Ready |
| Meta Dublin | Ireland | €100K-€160K | ✅ Resume Ready |
| SAP | Germany | €110K-€160K | ✅ Resume Ready |

### LinkedIn Easy Apply
- **Status**: Configured and ready
- **Config**: `linkedin_config.json` 
- **Safety**: Auto-submit disabled by default
- **Rate Limit**: 10 applications per session

## Key Features

### ✅ What's Working
1. **European job fetcher** - 10 positions with tailored resumes
2. **Master tracker integration** - Auto-updates CSV with new opportunities
3. **LinkedIn Easy Apply** - Selenium automation ready
4. **Tailored resumes** - Country-specific visa notes
5. **Batch processing** - Apply to multiple jobs efficiently

### 🎯 Unique Advantages
- All European jobs offer **visa sponsorship**
- Resumes emphasize **$1.2M savings** at Humana
- **10 years experience** prominently featured
- **Immediate relocation** availability stated
- **GDPR compliance** experience mentioned

## Next Actions

### Immediate (Today)
```bash
# 1. Apply to DeepMind (highest priority - UK visa)
python3 apply_to_european_jobs.py
# Select option 1

# 2. Apply to Spotify (Principal role - Sweden)
python3 apply_to_european_jobs.py
# Select option 9

# 3. Update LinkedIn for European visibility
# Add "Open to relocation to EU/UK" to headline
```

### This Week
- [ ] Apply to all 10 European positions
- [ ] Set up LinkedIn Easy Apply for batch processing
- [ ] Follow up on applications after 3 days
- [ ] Research additional European companies

## File Locations

### Resumes
- European: `resumes/european/`
- General: `resumes/`

### Databases
- European jobs: `data/european_jobs.db`
- LinkedIn jobs: `data/linkedin_jobs.db`

### Tracking
- Master CSV: `MASTER_TRACKER_400K.csv`
- Application log: `sent_applications_log.json`

## Usage Tips

### For European Applications
1. Run `python3 apply_to_european_jobs.py`
2. Select a job number to open careers page
3. Copy the tailored resume from `resumes/european/`
4. Apply directly on company website
5. Mention visa sponsorship need upfront

### For LinkedIn Easy Apply
1. Add job URLs to `linkedin_job_urls.txt`
2. Run `python3 linkedin_job_processor.py`
3. Review applications before auto-submit
4. Check `processed_linkedin_urls.json` for history

## Success Metrics
- **Target**: 50+ applications per week
- **European focus**: 10 visa-sponsored positions
- **Response rate goal**: 10-15%
- **Interview target**: 2-3 per week

---

*Last updated: 2025-08-21*
*Total automation scripts: 7*
*Total resumes generated: 10*