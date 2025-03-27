#!/usr/bin/env python3
"""
Load synthetic data into MySQL database.

This script reads CSV files from the data/ directory and loads them into the MySQL database
defined in the mysql_schema.sql file. It maintains the referential integrity between
patients, samples, and tests tables.
"""

import os
import csv
import mysql.connector
from pathlib import Path
from typing import List, Dict, Any
import argparse
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables or use defaults
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DATABASE", "genomics_db")

# Paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_FILE = PROJECT_ROOT / "mysql_schema.sql"

# CSV files
PATIENT_CSV = DATA_DIR / "patients.csv"
SAMPLE_CSV = DATA_DIR / "samples.csv"
TEST_CSV = DATA_DIR / "clinical_tests.csv"
PANEL_CSV = DATA_DIR / "test_panels.csv"
QUALITY_METRIC_CSV = DATA_DIR / "test_quality_metrics.csv"
PANEL_ASSIGNMENT_CSV = DATA_DIR / "test_panel_assignments.csv"

def connect_to_mysql() -> mysql.connector.connection.MySQLConnection:
    """
    Connect to MySQL database using environment variables.
    Returns a connection object.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            auth_plugin='mysql_native_password'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        sys.exit(1)

def create_database(conn: mysql.connector.connection.MySQLConnection) -> None:
    """
    Create the database if it doesn't exist.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        sys.exit(1)
    finally:
        cursor.close()

def use_database(conn: mysql.connector.connection.MySQLConnection) -> None:
    """
    Set the current database to use.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        print(f"Using database '{DB_NAME}'.")
    except mysql.connector.Error as err:
        print(f"Error selecting database: {err}")
        sys.exit(1)
    finally:
        cursor.close()

def execute_sql_script(conn: mysql.connector.connection.MySQLConnection, script_path: Path) -> None:
    """
    Execute an SQL script file.
    """
    cursor = conn.cursor()
    try:
        with open(script_path, 'r') as f:
            sql_script = f.read()
            
        # Split the script by semicolon to execute each statement separately
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print(f"Executed SQL script: {script_path}")
    except mysql.connector.Error as err:
        print(f"Error executing SQL script: {err}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"SQL script file not found: {script_path}")
        sys.exit(1)
    finally:
        cursor.close()

def read_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read a CSV file and return a list of dictionaries.
    """
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []
    
    data = []
    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert empty strings to None for NULL values
            for key, value in row.items():
                if value == '':
                    row[key] = None
            data.append(row)
    
    return data

def insert_data(conn: mysql.connector.connection.MySQLConnection, table: str, data: List[Dict[str, Any]]) -> None:
    """
    Insert data into a specified table.
    """
    if not data:
        print(f"No data to insert into {table}")
        return
    
    cursor = conn.cursor()
    try:
        # Get column names from the first row
        columns = list(data[0].keys())
        
        # Prepare the query
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        
        # Prepare the values for bulk insert
        values = []
        for row in data:
            row_values = [row[col] for col in columns]
            values.append(row_values)
        
        # Execute the query
        cursor.executemany(query, values)
        conn.commit()
        
        print(f"Inserted {len(data)} rows into {table}")
    except mysql.connector.Error as err:
        print(f"Error inserting data into {table}: {err}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    """
    Main function to load data into MySQL.
    """
    parser = argparse.ArgumentParser(description='Load synthetic data into MySQL database.')
    parser.add_argument('--no-create-schema', action='store_true', help='Skip creating the database schema')
    args = parser.parse_args()
    
    # Connect to MySQL
    print("Connecting to MySQL...")
    conn = connect_to_mysql()
    
    # Create and use the database
    create_database(conn)
    use_database(conn)
    
    # Create schema if necessary
    if not args.no_create_schema:
        print("Creating database schema...")
        execute_sql_script(conn, SCHEMA_FILE)
    
    # Read data from CSV files
    print("Reading data from CSV files...")
    patients = read_csv_file(PATIENT_CSV)
    samples = read_csv_file(SAMPLE_CSV)
    tests = read_csv_file(TEST_CSV)
    panels = read_csv_file(PANEL_CSV)
    quality_metrics = read_csv_file(QUALITY_METRIC_CSV)
    panel_assignments = read_csv_file(PANEL_ASSIGNMENT_CSV)
    
    # Insert data in order to maintain referential integrity
    print("Inserting data into MySQL...")
    insert_data(conn, "patients", patients)
    insert_data(conn, "samples", samples)
    insert_data(conn, "clinical_tests", tests)
    insert_data(conn, "test_panels", panels)
    insert_data(conn, "test_quality_metrics", quality_metrics)
    insert_data(conn, "test_panel_assignment", panel_assignments)
    
    # Close the connection
    conn.close()
    print("Data loading complete!")

if __name__ == "__main__":
    main() 