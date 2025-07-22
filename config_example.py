"""
Configuration example for the database migration script.
Copy this to config.py and modify as needed.
"""

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'port': 3306,
    'charset': 'utf8mb4'
}

# Source and target databases
SOURCE_DATABASE = 'economics'
TARGET_DATABASE = 'recruiting'

# Tables to bypass during migration
BYPASS_KEYWORDS = ['applications', 'candidates']

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'log_file': 'database_migration.log',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Migration settings
MIGRATION_SETTINGS = {
    'batch_size': 1000,  # For large table migrations
    'confirm_before_migration': True,
    'create_backup': False
}