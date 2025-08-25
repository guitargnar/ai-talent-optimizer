# 🤖 Puppeteer Integration for Greenhouse Automation

## Overview
This feature branch implements automated job applications for Greenhouse-based portals using MCP Puppeteer server.

## Implementation Status ✅

### Completed Features
1. **User Information Integration**
   - Pulls data from knowledge graph (Matthew Scott's details)
   - Pre-fills all standard Greenhouse form fields
   - Handles formatted and unformatted phone numbers

2. **Greenhouse Automation (`apply_via_greenhouse`)**
   - Navigate to job URL
   - Click "Apply Now" button
   - Fill application form fields
   - Attach resume (base_resume.pdf)
   - Take screenshot for review
   - Submit application (when not in dry run)

3. **Safety Features**
   - **Dry Run Mode** (default: `True`)
   - Screenshot capture before submission
   - Review mode to verify all fields
   - No accidental submissions

4. **Form Field Mapping**
   ```python
   Standard fields filled:
   - First Name: Matthew
   - Last Name: Scott
   - Email: matthewdscott7@gmail.com
   - Phone: (502) 345-0525
   - Location: Louisville, Kentucky
   - LinkedIn: linkedin.com/in/mscott77
   - GitHub: github.com/guitargnar
   - Cover Letter: [Personalized per application]
   ```

## Files Modified/Created

### Modified
- `web_form_automator.py` - Added full Greenhouse automation logic

### Created
- `test_greenhouse_automation.py` - Test suite for automation
- `puppeteer_greenhouse_integration.py` - Real Puppeteer integration demo
- `PUPPETEER_INTEGRATION_GUIDE.md` - This documentation

## Usage

### Basic Usage (Dry Run)
```python
from web_form_automator import WebFormAutomator

# Initialize in dry run mode (default)
automator = WebFormAutomator(dry_run=True)

# Apply to a job
success, message = automator.apply_via_greenhouse(
    job_url="https://job-boards.greenhouse.io/anthropic/jobs/5509568",
    cover_letter="Your personalized cover letter...",
    resume_path="resumes/base_resume.pdf"
)
```

### Live Submission
```python
# Initialize in live mode (actually submits!)
automator = WebFormAutomator(dry_run=False)

# This will submit the application for real
success, message = automator.apply_via_greenhouse(...)
```

## MCP Puppeteer Integration

### Required MCP Tools
The implementation uses these MCP Puppeteer server tools:

1. `mcp__puppeteer__puppeteer_navigate` - Navigate to job page
2. `mcp__puppeteer__puppeteer_click` - Click buttons
3. `mcp__puppeteer__puppeteer_fill` - Fill form fields
4. `mcp__puppeteer__puppeteer_screenshot` - Capture screenshots
5. `mcp__puppeteer__puppeteer_evaluate` - Execute JavaScript (for file uploads)

### Prerequisites
- MCP Puppeteer server must be running
- Screenshots directory must exist
- base_resume.pdf must be in resumes/ directory

## Testing

### Run Tests
```bash
# Test form field detection and dry run
python3 test_greenhouse_automation.py

# Test Puppeteer integration demo
python3 puppeteer_greenhouse_integration.py
```

### Test Output
- Verifies user information loading
- Tests form field mapping
- Simulates full application flow
- Creates screenshot for review

## Integration with Orchestrator

The orchestrator.py already has hooks for this:

```python
# In orchestrator.py line 524-530
if hasattr(self.web_automator, 'apply_via_greenhouse') and 'greenhouse' in portal_url:
    print("   🤖 Attempting automated Greenhouse application...")
    success = self.web_automator.apply_via_greenhouse(portal_url)
    if success:
        print("   ✅ Automated application submitted!")
```

## Supported Companies (Greenhouse)

Companies using Greenhouse that can be automated:
- Anthropic
- Stripe
- Airbnb
- Coinbase
- Snap Inc.
- DoorDash
- Many startups

## Safety Considerations

1. **Always test in dry run mode first**
2. **Review screenshots before live submission**
3. **Verify form fields are correctly mapped**
4. **Keep DISABLE_AUTO_SEND.txt active**
5. **Test with non-critical applications first**

## Next Steps

### Immediate
- [ ] Test with real Greenhouse job URL
- [ ] Verify MCP Puppeteer server connection
- [ ] Review generated screenshots

### Future Enhancements
- [ ] Add Lever platform support
- [ ] Add Workday platform support
- [ ] Implement CAPTCHA handling
- [ ] Add multi-step application support
- [ ] Create application tracking database

## Troubleshooting

### Common Issues

1. **MCP Puppeteer not responding**
   - Ensure MCP server is running
   - Check ~/.mcp/servers.yaml configuration

2. **Form fields not found**
   - Greenhouse may use different selectors
   - Add new selectors to field_mappings

3. **Screenshot not saving**
   - Ensure screenshots/ directory exists
   - Check file permissions

## Summary

The Puppeteer integration for Greenhouse is fully implemented with:
- ✅ User data from knowledge graph
- ✅ Form filling automation
- ✅ Resume attachment logic
- ✅ Dry run mode with screenshots
- ✅ Safety controls to prevent accidents
- ✅ Ready for testing with real jobs

**Status: Ready for Testing** 🚀