# Database Configuration
DATABASE_PATH = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/job_applications.db"
DATABASE_NAME = "job_applications.db"

def get_db_connection():
    import sqlite3
    return sqlite3.connect(DATABASE_PATH)
