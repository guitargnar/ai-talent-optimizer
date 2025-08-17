# Compliant Job Application System Guide

## System Overview
A transparent, controlled job application system that ensures full compliance with usage policies while helping you efficiently apply to relevant positions.

## Key Features

### 1. Preview System (`preview_applications.py`)
- Shows exactly what will be sent BEFORE sending
- Displays email subject, body, and attachments
- No surprises - you see everything first

### 2. Guided Workflow (`guided_apply.py`)
- Interactive approval for each application
- Options: Send, Skip, Edit, Save for Later
- Built-in safety limits (max 10 per session)
- Minimum 30-second delay between sends

### 3. Real Company Jobs
- 307 positions from Anthropic, Scale AI, Figma, etc.
- All emails go to official careers@ addresses
- Verified company emails (no job boards)
- High relevance scoring based on your background

## How to Use

### Step 1: Preview Applications
```bash
python preview_applications.py
```
- Review top opportunities
- See exact email content
- Check relevance scores
- No emails are sent at this stage

### Step 2: Send with Approval
```bash
python guided_apply.py
```
- Review each job individually
- See full email preview
- Approve, skip, or edit each one
- Applications sent only with your explicit approval

### Step 3: Track Results
```bash
python main.py status
```
- View sent applications
- Check for responses
- Monitor success rates

## Compliance Features

### ✅ Transparency
- Full preview before sending
- Clear recipient information
- Exact email content shown

### ✅ Control
- Manual approval required
- Edit capability for each email
- Skip option for any job
- Stop session anytime

### ✅ Quality Over Quantity
- Personalized content for each company
- Relevant positions only (65%+ match)
- Professional templates
- Appropriate resume variants

### ✅ Rate Limiting
- Max 10 applications per session
- 30-second minimum between sends
- Daily limit of 20 applications
- Prevents spam-like behavior

### ✅ Legitimate Use
- Only careers@ addresses
- Real job postings
- Truthful representation
- Professional communication

## Current Status

### Jobs Available
- **Anthropic**: 105 positions
- **Scale AI**: 59 positions
- **Figma**: 30 positions
- **Plus**: Many more tech companies

### Top Matches
1. Anthropic - AI Infrastructure roles (100% relevance)
2. Scale AI - ML Engineer positions (95% relevance)
3. Tempus - Healthcare AI roles (90% relevance)

## Safety Guidelines

### DO:
- Review each application before sending
- Personalize content when editing
- Track responses and adjust approach
- Respect any rejection or unsubscribe requests
- Focus on quality matches

### DON'T:
- Send without reviewing
- Use identical emails for multiple companies
- Exceed reasonable daily limits
- Apply to the same position twice
- Send to non-careers addresses

## Quick Start

1. **Test Email Configuration**
   ```bash
   python test_email_config.py
   ```

2. **Preview Top 5 Opportunities**
   ```bash
   python preview_applications.py
   # Enter: 5
   # Show details: y
   ```

3. **Send Your First Application**
   ```bash
   python guided_apply.py
   # Review the job
   # Check the email
   # Choose: 1 (SEND)
   # Confirm: yes
   ```

## Monitoring & Adjustments

### Daily Routine
- Morning: Review new opportunities
- Send 5-10 quality applications
- Evening: Check for responses
- Adjust templates based on feedback

### Weekly Tasks
- Refresh job listings
- Update resume if needed
- Review application metrics
- Refine targeting strategy

## Support & Troubleshooting

### Email Issues
- Ensure app password is correct
- Check Gmail for security alerts
- Verify 2FA is enabled
- Monitor sent folder

### No Jobs Found
- Run: `python load_real_company_jobs.py`
- Check database: `python main.py status`
- Verify email configuration

### Application Failures
- Check logs in `logs/` directory
- Verify internet connection
- Ensure email service is running
- Check for Gmail rate limits

## Ethical Commitment

This system is designed to:
- Respect companies' hiring processes
- Provide genuine value through quality applications
- Maintain professional standards
- Build meaningful connections
- Support legitimate job seeking

By using this system, you commit to:
- Honest representation of skills
- Professional communication
- Respectful engagement
- Quality over quantity approach

---

**Remember**: This tool amplifies your job search efficiency while maintaining the personal touch and professionalism that companies expect. Use it responsibly to find your next great opportunity!

*Last Updated: August 17, 2025*