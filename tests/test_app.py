import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
initial_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities_returns_activities():
    # Arrange
    expected_activities = {"Chess Club", "Programming Class"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activities.issubset(set(data.keys()))
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "testuser1@mergington.edu"
    signup_url = f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    signup_url = f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"

    # Act
    first_response = client.post(signup_url)
    second_response = client.post(signup_url)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_from_activity():
    # Arrange
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"
    signup_url = f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
    delete_url = f"/activities/{activity_name.replace(' ', '%20')}/participants?email={email}"

    # Act
    signup_response = client.post(signup_url)
    delete_response = client.delete(delete_url)

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"
    delete_url = f"/activities/{activity_name.replace(' ', '%20')}/participants?email={email}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
