#\!/usr/bin/env python3
"""Send One Test Application"""

from simple_apply import SimpleApplicationSender
import sqlite3

sender = SimpleApplicationSender()

# Get ONE job
conn = sqlite3.connect("REAL_JOBS.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT id, company, position, location, remote, 
           salary_min, salary_max, url, email
    FROM jobs
    WHERE applied = 0
    AND email IS NOT NULL
    AND position LIKE '%Staff%'
    LIMIT 1
""")
job = cursor.fetchone()
conn.close()

if job:
    job_id, company, position, location, remote, sal_min, sal_max, url, email = job
    print(f"Sending to: {company} - {position}")
    print(f"Email: {email}")
    sender.send_application(job_id, company, position, email)
else:
    print("No job found")
