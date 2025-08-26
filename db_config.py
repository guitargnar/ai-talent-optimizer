# Database Configuration
DATABASE_PATH = "unified_platform.db"
DATABASE_NAME = "unified_platform.db"

def get_db_connection():
    import sqlite3
    return sqlite3.connect(DATABASE_PATH)
