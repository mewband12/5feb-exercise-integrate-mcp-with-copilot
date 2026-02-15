# Database Setup Guide

This application uses MySQL for data persistence. Follow these steps to set up the database.

## Prerequisites

- MySQL Server 5.7 or higher
- Python 3.7 or higher

## Installation Steps

### 1. Install MySQL

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### On macOS:
```bash
brew install mysql
brew services start mysql
```

#### On Windows:
Download and install from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)

### 2. Configure MySQL

Start MySQL and create a database user (optional):

```bash
mysql -u root -p
```

Then run:
```sql
CREATE DATABASE school_management;
CREATE USER 'school_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON school_management.* TO 'school_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Set Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and update with your MySQL credentials:
```
DB_HOST=localhost
DB_USER=root  # or your MySQL user
DB_PASSWORD=your_password
DB_NAME=school_management
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database

Run the initialization script:
```bash
python init_db.py
```

This will:
- Create the database if it doesn't exist
- Create all required tables
- Seed initial data (users, clubs, students, memberships)

## Database Schema

### Tables

#### users
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password (using bcrypt)
- `role`: User role (admin/teacher)
- `created_at`: Timestamp

#### students
- `id`: Primary key
- `email`: Unique student email
- `name`: Student name (optional)
- `created_at`: Timestamp

#### clubs
- `id`: Primary key
- `name`: Unique club name
- `description`: Club description
- `schedule`: Meeting schedule
- `max_participants`: Maximum number of participants
- `created_at`: Timestamp

#### club_memberships
- `id`: Primary key
- `club_id`: Foreign key to clubs
- `student_id`: Foreign key to students
- `joined_at`: Timestamp
- Unique constraint on (club_id, student_id)

## Default Credentials

After initialization, you can login with:
- **Username:** admin, **Password:** school123
- **Username:** principal, **Password:** mergington2026
- **Username:** teacher1, **Password:** teacher123

## Running the Application

```bash
cd src
uvicorn app:app --reload
```

The application will be available at: http://localhost:8000

## Troubleshooting

### Connection Error
If you get a connection error:
1. Check MySQL is running: `sudo systemctl status mysql`
2. Verify credentials in `.env` file
3. Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Permission Denied
If you get permission errors:
1. Ensure MySQL user has proper privileges
2. Try connecting with root user initially

### Database Already Exists
The initialization script is idempotent - it will not recreate tables or duplicate data if run multiple times.

## Data Persistence

All data is now persisted in MySQL:
- User credentials
- Club/Activity information
- Student registrations
- Membership data

The application will automatically connect to the database on startup and maintain data across server restarts.
