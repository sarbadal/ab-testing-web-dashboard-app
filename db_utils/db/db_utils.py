"""
Database utilities for A/B Testing application.
Handles SQLite database creation, data ingestion, and querying.
"""

import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any

# Load environment variables
load_dotenv()


def db_print(*args, **kwargs):
    """Print function that respects DB_VERBOSE environment variable."""
    db_verbose = os.getenv('DB_VERBOSE', 'True').lower() == 'true'
    if db_verbose:
        print(*args, **kwargs)


class ABTestingDB:
    """Class to handle A/B Testing database operations."""

    def __init__(self, db_path: str = None, table_name: str = "ab_test_data"):
        """Initialize database connection. """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.db_path = project_root / "app" / "data.db"
        else:
            self.db_path = Path(db_path)
        
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to SQLite database."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.cursor = self.connection.cursor()
            db_print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            db_print(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            db_print("Database connection closed.")
    
    def __enter__(self):
        """Context manager entry point."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()
        # Return None to propagate any exceptions
        return None
    
    def create_tables(self):
        """Create tables for A/B testing data."""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id INTEGER NOT NULL,
            test_group TEXT NOT NULL,
            visit_date DATE NOT NULL,
            device_type TEXT NOT NULL,
            location TEXT NOT NULL,
            visitor_type TEXT NOT NULL,
            converted INTEGER NOT NULL CHECK (converted IN (0, 1)),
            order_value REAL NOT NULL DEFAULT 0,
            bounce INTEGER NOT NULL CHECK (bounce IN (0, 1)),
            pages_session INTEGER NOT NULL,
            select_test TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            db_print("Table 'ab_test_data' created successfully.")
        except sqlite3.Error as e:
            db_print(f"Error creating table: {e}")
            raise
    
    def ingest_csv_data(self, csv_path: str = None):
        """
        Ingest data from CSV file into the database.
        
        Args:
            csv_path: Path to CSV file. If None, uses default location.
        """
        if csv_path is None:
            # Default CSV path
            csv_path = Path(__file__).parent.parent / "data" / "raw_data.csv"
        else:
            csv_path = Path(csv_path)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        try:
            # Read CSV data
            df = pd.read_csv(csv_path)
            db_print(f"Read {len(df)} rows from {csv_path}")
            
            # Clear existing data (optional - remove if you want to append)
            self.cursor.execute("DELETE FROM ab_test_data")
            
            # Insert data into database
            df.to_sql('ab_test_data', self.connection, if_exists='append', index=False)
            self.connection.commit()
            
            db_print(f"Successfully ingested {len(df)} rows into the database.")
            
            # Verify data insertion
            self.cursor.execute("SELECT COUNT(*) FROM ab_test_data")
            count = self.cursor.fetchone()[0]
            db_print(f"Total rows in database: {count}")
            
        except Exception as e:
            db_print(f"Error ingesting CSV data: {e}")
            self.connection.rollback()
            raise
    
    def get_test_summary(self, test_name: str = None) -> List[Dict[str, Any]]:
        """
        Get summary statistics for A/B tests.
        
        Args:
            test_name: Specific test name to filter by. If None, returns all tests.
        
        Returns:
            List of dictionaries containing test summary data.
        """
        if test_name:
            query = """
            SELECT 
                select_test,
                test_group,
                COUNT(*) as total_visitors,
                SUM(converted) as conversions,
                ROUND(AVG(converted) * 100, 2) as conversion_rate,
                ROUND(AVG(order_value), 2) as avg_order_value,
                ROUND(AVG(bounce) * 100, 2) as bounce_rate,
                ROUND(AVG(pages_session), 2) as avg_pages_per_session
            FROM ab_test_data 
            WHERE select_test = ?
            GROUP BY select_test, test_group
            ORDER BY select_test, test_group
            """
            params = (test_name,)
        else:
            query = """
            SELECT 
                select_test,
                test_group,
                COUNT(*) as total_visitors,
                SUM(converted) as conversions,
                ROUND(AVG(converted) * 100, 2) as conversion_rate,
                ROUND(AVG(order_value), 2) as avg_order_value,
                ROUND(AVG(bounce) * 100, 2) as bounce_rate,
                ROUND(AVG(pages_session), 2) as avg_pages_per_session
            FROM ab_test_data 
            GROUP BY select_test, test_group
            ORDER BY select_test, test_group
            """
            params = ()
        
        try:
            self.cursor.execute(query, params)
            columns = [description[0] for description in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except sqlite3.Error as e:
            db_print(f"Error querying database: {e}")
            return []
    
    def get_device_performance(self) -> List[Dict[str, Any]]:
        """Get performance metrics by device type."""
        query = """
        SELECT 
            device_type,
            test_group,
            COUNT(*) as total_visitors,
            ROUND(AVG(converted) * 100, 2) as conversion_rate,
            ROUND(AVG(order_value), 2) as avg_order_value
        FROM ab_test_data 
        GROUP BY device_type, test_group
        ORDER BY device_type, test_group
        """
        
        try:
            self.cursor.execute(query)
            columns = [description[0] for description in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except sqlite3.Error as e:
            db_print(f"Error querying device performance: {e}")
            return []
    
    def get_visitor_type_analysis(self) -> List[Dict[str, Any]]:
        """Get analysis by visitor type (New vs Returning)."""
        query = """
        SELECT 
            visitor_type,
            test_group,
            COUNT(*) as total_visitors,
            ROUND(AVG(converted) * 100, 2) as conversion_rate,
            ROUND(AVG(order_value), 2) as avg_order_value
        FROM ab_test_data 
        GROUP BY visitor_type, test_group
        ORDER BY visitor_type, test_group
        """
        
        try:
            self.cursor.execute(query)
            columns = [description[0] for description in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except sqlite3.Error as e:
            db_print(f"Error querying visitor type analysis: {e}")
            return []


def setup_database():
    """
    Main function to set up the database and ingest initial data.
    This function can be run standalone to initialize the database.
    """
    db_print("Setting up A/B Testing database...")
    
    # Initialize database
    db = ABTestingDB()
    
    try:
        # Connect to database
        db.connect()
        
        # Create tables
        db.create_tables()
        
        # Ingest CSV data
        db.ingest_csv_data()
        
        # Test queries
        db_print("\n=== Test Summary ===")
        summary = db.get_test_summary()
        for row in summary[:5]:  # Show first 5 rows
            db_print(row)
        
        db_print("\n=== Device Performance ===")
        device_perf = db.get_device_performance()
        for row in device_perf[:3]:  # Show first 3 rows
            db_print(row)
        
    except Exception as e:
        db_print(f"Setup failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # Run database setup when script is executed directly
    setup_database()
