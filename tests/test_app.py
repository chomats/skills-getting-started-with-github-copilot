import copy

import pytest
from fastapi.testclient import TestClient

from app import app, activities as activities_data

client = TestClient(app)

initial_activities = copy.deepcopy(activities_data)


@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities_data.clear()
    activities_data.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_success():
    email = "test.student@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_returns_error():
    email = "michael@mergington.edu"
    first_response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert first_response.status_code == 400

    second_response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    response = client.post("/activities/Unknown/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess Club/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities_data["Chess Club"]["participants"]


def test_remove_participant_not_found_returns_error():
    response = client.delete("/activities/Chess Club/participants?email=unknown@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found"


def test_remove_activity_not_found_returns_404():
    response = client.delete("/activities/Unknown/participants?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
