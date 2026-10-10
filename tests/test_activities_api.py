from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    # Arrange
    activity = "Basketball Team"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in app_module.activities[activity]["participants"]


def test_duplicate_signup_is_rejected_without_changing_participants(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = app_module.activities[activity]["participants"].copy()

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert app_module.activities[activity]["participants"] == original_participants


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity = "Unknown Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_unknown_participant_returns_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "unknown@mergington.edu"
    original_participants = app_module.activities[activity]["participants"].copy()

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"
    assert app_module.activities[activity]["participants"] == original_participants


def test_unregister_from_unknown_activity_returns_not_found(client):
    # Arrange
    activity = "Unknown Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"