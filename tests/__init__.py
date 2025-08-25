"""
Test suite for Career Automation System
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
TEST_ENV_FILE = Path(__file__).parent / ".env.test"
TEST_DB_FILE = Path(__file__).parent / "test_jobs.db"
