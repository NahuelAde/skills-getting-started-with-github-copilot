import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # FastAPI TestClient follows redirects
    assert "text/html" in response.headers["content-type"]

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Test structure of an activity
    activity = list(data.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already exists in Chess Club
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()

def test_signup_nonexistent_activity():
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_unregister_success():
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"  # Existing participant
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregistered" in data["message"].lower()
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()

def test_unregister_nonexistent_activity():
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()