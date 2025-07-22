#!/usr/bin/env python3
"""
Database Table Migration Script

This script migrates recruit tables from the economics database to the recruiting database
for a new academic year, with improved error handling and security practices.
"""

import pymysql
import sys
import logging
import os
from contextlib import contextmanager
from typing import List, Tuple
import getpass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database migration operations with improved error handling and security."""
    
    def __init__(self, host: str = 'localhost', user: str = 'root'):
        self.host = host
        self.user = user
        self.password = None
        self.connection = None
    
    def get_credentials(self):
        """Securely get database credentials."""
        # Try to get password from environment variable first
        self.password = os.getenv('DB_PASSWORD')
        
        if not self.password:
            self.password = getpass.getpass("Enter database password: ")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                autocommit=False
            )
            logger.info("Database connection established")
            yield self.connection
        except pymysql.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed")
    
    def get_academic_years(self) -> Tuple[str, str]:
        """Get academic year input with validation."""
        while True:
            try:
                next_year = input("Enter the next academic year (e.g., 2024): ").strip()
                prev_year = input("Enter the previous academic year (e.g., 2023): ").strip()
                
                # Basic validation
                if not next_year.isdigit() or not prev_year.isdigit():
                    raise ValueError("Years must be numeric")
                
                if int(next_year) <= int(prev_year):
                    raise ValueError("Next year must be greater than previous year")
                
                return next_year, prev_year
                
            except ValueError as e:
                logger.error(f"Invalid input: {e}")
                print(f"Error: {e}. Please try again.")
    
    def get_recruit_tables(self, cursor) -> List[str]:
        """Get all recruit tables from the economics database."""
        try:
            cursor.execute("SHOW TABLES FROM economics LIKE %s", ('%recruit%',))
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            logger.info(f"Found {len(table_names)} recruit tables: {table_names}")
            return table_names
        except pymysql.Error as e:
            logger.error(f"Error fetching tables: {e}")
            raise
    
    def should_bypass_table(self, table_name: str) -> bool:
        """Check if table should be bypassed based on naming conventions."""
        bypass_keywords = ['applications', 'candidates']
        return any(keyword in table_name.lower() for keyword in bypass_keywords)
    
    def create_and_populate_table(self, cursor, table_name: str, next_year: str):
        """Create and populate a new table in the recruiting database."""
        try:
            new_table_name = f"{table_name}_{next_year}"
            
            # Create table structure
            create_sql = f"CREATE TABLE recruiting.{new_table_name} LIKE economics.{table_name}"
            cursor.execute(create_sql)
            logger.info(f"Created table: recruiting.{new_table_name}")
            
            # Copy data
            insert_sql = f"INSERT INTO recruiting.{new_table_name} SELECT * FROM economics.{table_name}"
            cursor.execute(insert_sql)
            
            # Get row count
            count_sql = f"SELECT COUNT(*) FROM recruiting.{new_table_name}"
            cursor.execute(count_sql)
            row_count = cursor.fetchone()[0]
            
            logger.info(f"Copied {row_count} rows to recruiting.{new_table_name}")
            return row_count
            
        except pymysql.Error as e:
            logger.error(f"Error processing table {table_name}: {e}")
            raise
    
    def migrate_tables(self):
        """Main migration process."""
        try:
            # Get credentials and academic years
            self.get_credentials()
            next_year, prev_year = self.get_academic_years()
            
            logger.info(f"Starting migration from {prev_year} to {next_year}")
            
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Get all recruit tables
                table_names = self.get_recruit_tables(cursor)
                
                if not table_names:
                    logger.warning("No recruit tables found")
                    return
                
                processed_tables = 0
                bypassed_tables = 0
                
                for table_name in table_names:
                    if self.should_bypass_table(table_name):
                        logger.info(f"Bypassing table: {table_name}")
                        bypassed_tables += 1
                        continue
                    
                    try:
                        row_count = self.create_and_populate_table(cursor, table_name, next_year)
                        processed_tables += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to process table {table_name}: {e}")
                        # Ask user if they want to continue
                        response = input(f"Continue with remaining tables? (y/n): ").lower()
                        if response != 'y':
                            break
                
                # Commit all changes
                connection.commit()
                logger.info(f"Migration completed successfully!")
                logger.info(f"Processed: {processed_tables} tables, Bypassed: {bypassed_tables} tables")
                
        except KeyboardInterrupt:
            logger.info("Migration cancelled by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        migrator = DatabaseMigrator()
        migrator.migrate_tables()
        print("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()