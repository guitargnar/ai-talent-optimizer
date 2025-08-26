#!/usr/bin/env python3
"""
Database Connection Helper
=========================

Provides unified database access for AI Talent Optimizer.
All components should use this module for database connectivity.
"""

import sqlite3
import os
from contextlib import contextmanager

# Unified database configuration
DATABASE_PATH = "unified_platform.db"

def get_connection():
    """Get a connection to the unified database."""
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(f"Unified database not found: {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

@contextmanager
def get_cursor():
    """Context manager for database operations."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor, conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def quick_query(sql, params=None):
    """Execute a quick query and return results."""
    with get_cursor() as (cursor, conn):
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()

def quick_count(table):
    """Get record count for a table."""
    with get_cursor() as (cursor, conn):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]

def get_job_by_company_position(company, title):
    """Find job by company and position."""
    return quick_query(
        "SELECT * FROM jobs WHERE company = ? AND title = ?", 
        (company, title)
    )

def get_applications_by_status(status='sent'):
    """Get applications by status."""
    return quick_query(
        "SELECT * FROM applications WHERE status = ?", 
        (status,)
    )

def get_recent_responses(limit=10):
    """Get recent responses."""
    return quick_query(
        "SELECT * FROM emails ORDER BY received_date DESC LIMIT ?", 
        (limit,)
    )

def get_system_stats():
    """Get overall system statistics."""
    return {
        'jobs': quick_count('jobs'),
        'applications': quick_count('applications'), 
        'responses': quick_count('responses'),
        'contacts': quick_count('contacts'),
        'metrics': quick_count('metrics')
    }

if __name__ == "__main__":
    # Test the connection
    try:
        stats = get_system_stats()
        print("Database Connection Test:")
        print(f"  Database: {DATABASE_PATH}")
        for table, count in stats.items():
            print(f"  {table}: {count} records")
        print("✅ Connection successful!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
