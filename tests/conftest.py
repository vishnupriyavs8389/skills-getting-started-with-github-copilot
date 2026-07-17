import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """Create a test FastAPI app with isolated in-memory data"""
    app = FastAPI()
    
    # Create isolated activities data for testing
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Art Class": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    
    @app.get("/")
    def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/index.html")
    
    @app.get("/activities")
    def get_activities():
        return test_activities
    
    @app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = test_activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student is already signed up for this activity")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @app.delete("/activities/{activity_name}/participants/{email}")
    def remove_participant(activity_name: str, email: str):
        """Remove a participant from an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = test_activities[activity_name]
        
        if email not in activity["participants"]:
            raise HTTPException(status_code=404, detail="Participant not found")
        
        activity["participants"].remove(email)
        return {"message": f"Removed {email} from {activity_name}"}
    
    return app


@pytest.fixture
def client(app):
    """Create a TestClient instance for the app"""
    return TestClient(app)
