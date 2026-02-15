#!/usr/bin/env python3
"""
Database initialization script.
Run this script to set up the database schema and seed initial data.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import db

def main():
    print("Initializing database...")
    
    # Connect to database
    if not db.connect():
        print("Failed to connect to database. Please check your database configuration.")
        print("Make sure MySQL is running and environment variables are set correctly.")
        sys.exit(1)
    
    # Initialize schema
    print("Creating database schema...")
    if not db.init_database():
        print("Failed to initialize database schema.")
        sys.exit(1)
    
    # Seed initial data
    print("Seeding initial data...")
    db.seed_initial_data()
    
    # Close connection
    db.disconnect()
    
    print("\n✓ Database initialization complete!")
    print("\nDefault users created:")
    print("  - Username: admin, Password: school123")
    print("  - Username: principal, Password: mergington2026")
    print("  - Username: teacher1, Password: teacher123")

if __name__ == "__main__":
    main()
