"""
Database connection and operations module for MySQL persistence.
"""

import mysql.connector
from mysql.connector import Error
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class Database:
    """Database manager for MySQL operations."""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'school_management')
        }
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"Connected to MySQL database: {self.config['database']}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Get a database cursor with automatic commit/rollback."""
        cursor = self.connection.cursor(dictionary=dictionary)
        try:
            yield cursor
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def init_database(self):
        """Initialize database with schema."""
        # First connect without database to create it if needed
        temp_config = self.config.copy()
        db_name = temp_config.pop('database')
        
        try:
            temp_conn = mysql.connector.connect(**temp_config)
            cursor = temp_conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'teacher',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create students table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create clubs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clubs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    schedule VARCHAR(255),
                    max_participants INT DEFAULT 20,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create club_memberships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS club_memberships (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    club_id INT NOT NULL,
                    student_id INT NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_membership (club_id, student_id)
                )
            """)
            
            temp_conn.commit()
            cursor.close()
            temp_conn.close()
            
            print("Database schema initialized successfully")
            return True
            
        except Error as e:
            print(f"Error initializing database: {e}")
            return False
    
    def seed_initial_data(self):
        """Seed database with initial data."""
        with self.get_cursor() as cursor:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()['count'] > 0:
                print("Database already seeded")
                return
            
            # Insert initial users (teachers)
            teachers = [
                ('admin', 'school123', 'admin'),
                ('principal', 'mergington2026', 'admin'),
                ('teacher1', 'teacher123', 'teacher')
            ]
            cursor.executemany(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                teachers
            )
            
            # Insert initial clubs
            clubs = [
                ('Chess Club', 'Learn strategies and compete in chess tournaments', 
                 'Fridays, 3:30 PM - 5:00 PM', 12),
                ('Programming Class', 'Learn programming fundamentals and build software projects',
                 'Tuesdays and Thursdays, 3:30 PM - 4:30 PM', 20),
                ('Gym Class', 'Physical education and sports activities',
                 'Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM', 30),
                ('Soccer Team', 'Join the school soccer team and compete in matches',
                 'Tuesdays and Thursdays, 4:00 PM - 5:30 PM', 22),
                ('Basketball Team', 'Practice and play basketball with the school team',
                 'Wednesdays and Fridays, 3:30 PM - 5:00 PM', 15),
                ('Art Club', 'Explore your creativity through painting and drawing',
                 'Thursdays, 3:30 PM - 5:00 PM', 15),
                ('Drama Club', 'Act, direct, and produce plays and performances',
                 'Mondays and Wednesdays, 4:00 PM - 5:30 PM', 20),
                ('Math Club', 'Solve challenging problems and participate in math competitions',
                 'Tuesdays, 3:30 PM - 4:30 PM', 10),
                ('Debate Team', 'Develop public speaking and argumentation skills',
                 'Fridays, 4:00 PM - 5:30 PM', 12)
            ]
            cursor.executemany(
                "INSERT INTO clubs (name, description, schedule, max_participants) VALUES (%s, %s, %s, %s)",
                clubs
            )
            
            # Insert initial students
            students = [
                'michael@mergington.edu', 'daniel@mergington.edu',
                'emma@mergington.edu', 'sophia@mergington.edu',
                'john@mergington.edu', 'olivia@mergington.edu',
                'liam@mergington.edu', 'noah@mergington.edu',
                'ava@mergington.edu', 'mia@mergington.edu',
                'amelia@mergington.edu', 'harper@mergington.edu',
                'ella@mergington.edu', 'scarlett@mergington.edu',
                'james@mergington.edu', 'benjamin@mergington.edu',
                'charlotte@mergington.edu', 'henry@mergington.edu'
            ]
            cursor.executemany(
                "INSERT INTO students (email) VALUES (%s)",
                [(email,) for email in students]
            )
            
            # Insert initial memberships
            memberships = [
                ('Chess Club', 'michael@mergington.edu'),
                ('Chess Club', 'daniel@mergington.edu'),
                ('Programming Class', 'emma@mergington.edu'),
                ('Programming Class', 'sophia@mergington.edu'),
                ('Gym Class', 'john@mergington.edu'),
                ('Gym Class', 'olivia@mergington.edu'),
                ('Soccer Team', 'liam@mergington.edu'),
                ('Soccer Team', 'noah@mergington.edu'),
                ('Basketball Team', 'ava@mergington.edu'),
                ('Basketball Team', 'mia@mergington.edu'),
                ('Art Club', 'amelia@mergington.edu'),
                ('Art Club', 'harper@mergington.edu'),
                ('Drama Club', 'ella@mergington.edu'),
                ('Drama Club', 'scarlett@mergington.edu'),
                ('Math Club', 'james@mergington.edu'),
                ('Math Club', 'benjamin@mergington.edu'),
                ('Debate Team', 'charlotte@mergington.edu'),
                ('Debate Team', 'henry@mergington.edu')
            ]
            
            for club_name, student_email in memberships:
                cursor.execute("""
                    INSERT INTO club_memberships (club_id, student_id)
                    SELECT c.id, s.id
                    FROM clubs c, students s
                    WHERE c.name = %s AND s.email = %s
                """, (club_name, student_email))
            
            print("Initial data seeded successfully")
    
    # User operations
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password, role FROM users WHERE username = %s",
                (username,)
            )
            return cursor.fetchone()
    
    # Club operations
    def get_all_clubs(self) -> List[Dict[str, Any]]:
        """Get all clubs with participant information."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.description,
                    c.schedule,
                    c.max_participants,
                    GROUP_CONCAT(s.email) as participants
                FROM clubs c
                LEFT JOIN club_memberships cm ON c.id = cm.club_id
                LEFT JOIN students s ON cm.student_id = s.id
                GROUP BY c.id, c.name, c.description, c.schedule, c.max_participants
            """)
            return cursor.fetchall()
    
    def get_club_by_name(self, club_name: str) -> Optional[Dict[str, Any]]:
        """Get club by name with participants."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.description,
                    c.schedule,
                    c.max_participants,
                    GROUP_CONCAT(s.email) as participants
                FROM clubs c
                LEFT JOIN club_memberships cm ON c.id = cm.club_id
                LEFT JOIN students s ON cm.student_id = s.id
                WHERE c.name = %s
                GROUP BY c.id, c.name, c.description, c.schedule, c.max_participants
            """, (club_name,))
            return cursor.fetchone()
    
    # Student operations
    def get_or_create_student(self, email: str) -> int:
        """Get student ID or create if doesn't exist."""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT id FROM students WHERE email = %s", (email,))
            result = cursor.fetchone()
            
            if result:
                return result['id']
            
            cursor.execute("INSERT INTO students (email) VALUES (%s)", (email,))
            return cursor.lastrowid
    
    def is_student_registered(self, club_id: int, student_id: int) -> bool:
        """Check if student is registered for a club."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM club_memberships WHERE club_id = %s AND student_id = %s",
                (club_id, student_id)
            )
            return cursor.fetchone()['count'] > 0
    
    def register_student(self, club_id: int, student_id: int) -> bool:
        """Register a student for a club."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO club_memberships (club_id, student_id) VALUES (%s, %s)",
                (club_id, student_id)
            )
            return True
    
    def unregister_student(self, club_id: int, student_id: int) -> bool:
        """Unregister a student from a club."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM club_memberships WHERE club_id = %s AND student_id = %s",
                (club_id, student_id)
            )
            return cursor.rowcount > 0


# Global database instance
db = Database()
