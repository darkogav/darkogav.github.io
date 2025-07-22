#!/usr/bin/env python3

import pymysql
import sys
import getpass

def main():
    # Get user input
    next_year = input("Enter the next academic year: ")
    prev_year = input("Enter the previous academic year: ")
    
    # Get database password securely
    password = getpass.getpass("Enter database password: ")
    
    try:
        # Connect to database
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=password,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Find all recruit tables
        cursor.execute("SHOW TABLES FROM economics LIKE '%recruit%'")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} recruit tables")
        
        for table in tables:
            table_name = table[0]
            
            # Skip applications and candidates tables
            if 'applications' in table_name or 'candidates' in table_name:
                print(f"Skipping: {table_name}")
                continue
            
            print(f"Processing: {table_name}")
            
            # Create new table in recruiting database
            cursor.execute(f"CREATE TABLE recruiting.{table_name} LIKE economics.{table_name}")
            
            # Copy data
            cursor.execute(f"INSERT INTO recruiting.{table_name} SELECT * FROM economics.{table_name}")
            
            # Show count
            cursor.execute(f"SELECT COUNT(*) FROM recruiting.{table_name}")
            count = cursor.fetchone()[0]
            print(f"  Copied {count} rows")
        
        print("Done!")
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()