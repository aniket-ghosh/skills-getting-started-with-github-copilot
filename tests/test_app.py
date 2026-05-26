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
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_activity_adds_participant():
    email = "testuser1@mergington.edu"
    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "duplicate@mergington.edu"
    first_response = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_from_activity():
    email = "removeme@mergington.edu"
    signup_response = client.post(
        f"/activities/Gym%20Class/signup?email={email}"
    )
    assert signup_response.status_code == 200

    delete_response = client.delete(
        f"/activities/Gym%20Class/participants?email={email}"
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from Gym Class"
    assert email not in app_module.activities["Gym Class"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/participants?email=unknown@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
