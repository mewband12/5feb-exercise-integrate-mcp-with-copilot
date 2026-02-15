"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Response, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
import os
import json
from pathlib import Path
import uuid
from database import db

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Session storage (in-memory for simplicity)
active_sessions = {}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and schema on startup."""
    if db.connect():
        db.init_database()
        db.seed_initial_data()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    db.disconnect()

# Authentication helper functions
def create_session(username: str) -> str:
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {"username": username}
    return session_id

def get_session(request: Request) -> dict:
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    return None

def require_admin(request: Request):
    session = get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities from database."""
    clubs = db.get_all_clubs()
    
    # Convert to the format expected by the frontend
    activities = {}
    for club in clubs:
        participants = []
        if club['participants']:
            participants = club['participants'].split(',')
        
        activities[club['name']] = {
            'description': club['description'],
            'schedule': club['schedule'],
            'max_participants': club['max_participants'],
            'participants': participants
        }
    
    return activities


# Authentication endpoints
@app.post("/auth/login")
def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    """Login endpoint for teachers"""
    user = db.get_user_by_username(username)
    if user and db.verify_password(password, user['password']):
        session_id = create_session(username)
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=86400)  # 24 hours
        return {"message": "Login successful", "username": username}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/auth/logout")
def logout(request: Request, response: Response):
    """Logout endpoint"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        del active_sessions[session_id]
    response.delete_cookie("session_id")
    return {"message": "Logout successful"}


@app.get("/auth/status")
def auth_status(request: Request):
    """Check if user is authenticated"""
    session = get_session(request)
    if session:
        return {"authenticated": True, "username": session["username"]}
    else:
        return {"authenticated": False}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, request: Request, admin_session=Depends(require_admin)):
    """Sign up a student for an activity - requires admin authentication"""
    # Validate activity exists
    club = db.get_club_by_name(activity_name)
    if not club:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get or create student
    student_id = db.get_or_create_student(email)
    
    # Validate student is not already signed up
    if db.is_student_registered(club['id'], student_id):
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Register student
    db.register_student(club['id'], student_id)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, request: Request, admin_session=Depends(require_admin)):
    """Unregister a student from an activity - requires admin authentication"""
    # Validate activity exists
    club = db.get_club_by_name(activity_name)
    if not club:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get or create student
    student_id = db.get_or_create_student(email)
    
    # Validate student is signed up
    if not db.is_student_registered(club['id'], student_id):
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Unregister student
    db.unregister_student(club['id'], student_id)
    return {"message": f"Unregistered {email} from {activity_name}"}
