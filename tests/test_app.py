"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to their initial state before each test."""
    original_participants = {name: list(details["participants"]) for name, details in activities.items()}
    yield
    for name, details in activities.items():
        details["participants"] = original_participants[name]


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]

        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestSignupForActivity:
    def test_signup_returns_200(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_signup_adds_student_to_participants(self, client):
        # Arrange
        email = "teststudent@mergington.edu"
        activity = "Programming Class"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        activities_response = client.get("/activities").json()

        # Assert
        assert email in activities_response[activity]["participants"]

    def test_signup_returns_confirmation_message(self, client):
        # Arrange
        email = "another@mergington.edu"
        activity = "Gym Class"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert "message" in response.json()
        assert email in response.json()["message"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_duplicate_signup_returns_400(self, client):
        # Arrange - michael is already in Chess Club
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_when_activity_is_full_returns_400(self, client):
        # Arrange - fill up Chess Club (max 12 participants, currently 2)
        activity = "Chess Club"
        for i in range(10):
            client.post(f"/activities/{activity}/signup?email=student{i}@mergington.edu")

        # Act - try to add one more
        response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    def test_unregister_returns_200(self, client):
        # Arrange - michael is already in Chess Club
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_student_from_participants(self, client):
        # Arrange - michael is already in Chess Club
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")
        activities_response = client.get("/activities").json()

        # Assert
        assert email not in activities_response[activity]["participants"]

    def test_unregister_returns_confirmation_message(self, client):
        # Arrange - michael is already in Chess Club
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert "message" in response.json()
        assert email in response.json()["message"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_student_not_signed_up_returns_404(self, client):
        # Arrange
        email = "notsignedup@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
