#!/usr/bin/env python3

import pymysql
import sys
import getpass

def main():
    # Get database password
    password = getpass.getpass("Enter database password: ")
    
    try:
        # Connect to database
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=password
        )
        cursor = conn.cursor()
        
        # Step 1: Find all tables ending with 2425 in economics database
        cursor.execute("SHOW TABLES FROM economics LIKE '%2425'")
        tables_2425 = cursor.fetchall()
        
        print(f"Found {len(tables_2425)} tables ending with 2425")
        
        # Step 2: Copy each 2425 table from economics to recruiting (with data)
        for table in tables_2425:
            table_name = table[0]
            print(f"Copying {table_name} to recruiting database...")
            
            # Create table structure in recruiting database
            cursor.execute(f"CREATE TABLE recruiting.{table_name} LIKE economics.{table_name}")
            
            # Copy all data
            cursor.execute(f"INSERT INTO recruiting.{table_name} SELECT * FROM economics.{table_name}")
            
            # Show count
            cursor.execute(f"SELECT COUNT(*) FROM recruiting.{table_name}")
            count = cursor.fetchone()[0]
            print(f"  Copied {count} rows")
        
        # Step 3: Create empty 2526 tables with same structure
        print("\nCreating empty 2526 tables...")
        for table in tables_2425:
            old_table_name = table[0]
            new_table_name = old_table_name.replace('2425', '2526')
            
            print(f"Creating empty table: {new_table_name}")
            cursor.execute(f"CREATE TABLE recruiting.{new_table_name} LIKE recruiting.{old_table_name}")
        
        print(f"\nDone! Copied {len(tables_2425)} tables and created {len(tables_2425)} new empty tables.")
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()