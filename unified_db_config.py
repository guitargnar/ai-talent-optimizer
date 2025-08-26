#!/usr/bin/env python3
"""
Unified Database Configuration
==============================
Central configuration for the unified platform database.
"""

import os
from pathlib import Path

# Database Configuration
UNIFIED_DB_PATH = os.environ.get('UNIFIED_DB_PATH', 'unified_platform.db')
UNIFIED_DB = Path(UNIFIED_DB_PATH)

# Ensure database exists
if not UNIFIED_DB.exists():
    raise FileNotFoundError(f"Unified database not found: {UNIFIED_DB}")

# Table names
class Tables:
    COMPANIES = 'companies'
    JOBS = 'jobs'
    APPLICATIONS = 'applications'
    CONTACTS = 'contacts'
    EMAILS = 'emails'
    METRICS = 'metrics'
    PROFILE = 'profile'
    SYSTEM_LOG = 'system_log'

# View names
class Views:
    ACTIVE_JOBS = 'active_jobs'
    APPLICATION_RESPONSES = 'application_responses'
    CONTACT_NETWORK = 'contact_network'

def get_connection():
    """Get a connection to the unified database."""
    import sqlite3
    return sqlite3.connect(str(UNIFIED_DB))

def get_db_path():
    """Get the path to the unified database."""
    return str(UNIFIED_DB)
