import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Utility to reset activities state between tests
@pytest.fixture(autouse=True)
def reset_activities():
    for activity in activities.values():
        activity["participants"].clear()
    # Add initial participants for tests that expect them
    activities["Chess Club"]["participants"].extend([
        "michael@mergington.edu", "daniel@mergington.edu"
    ])
    activities["Programming Class"]["participants"].extend([
        "emma@mergington.edu", "sophia@mergington.edu"
    ])
    activities["Gym Class"]["participants"].extend([
        "john@mergington.edu", "olivia@mergington.edu"
    ])
    yield

# --- Tests ---

def test_get_activities():
    # Arrange done by fixture
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_for_activity():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Art Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in response.json()["message"]

def test_signup_duplicate():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_for_activity():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert "Removed" in response.json()["message"]

def test_unregister_not_registered():
    # Arrange
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
