import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successful fetch of all activities"""
        # Arrange - test client is set up via fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Art Class" in activities
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that activities contain all required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_participant_count(self, client):
        """Test that participant counts are accurate"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == 2
        assert len(activities["Programming Class"]["participants"]) == 1
        assert len(activities["Art Class"]["participants"]) == 0


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Art Class"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
    
    def test_signup_duplicate_fails(self, client):
        """Test that duplicate signup returns 400 error"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for non-existent activity returns 404 error"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_adds_to_participant_list(self, client):
        """Test that signup properly adds email to participant list"""
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        original_count = 1  # Programming Class has 1 participant
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify count increased
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity_name]["participants"])
        assert new_count == original_count + 1
        assert email in activities_response.json()[activity_name]["participants"]


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
    
    def test_remove_participant_from_nonexistent_activity_fails(self, client):
        """Test that removing from non-existent activity returns 404 error"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing non-existent participant returns 404 error"""
        # Arrange
        activity_name = "Chess Club"
        email = "notaparticipant@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_participant_decreases_count(self, client):
        """Test that removing a participant decreases the count"""
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        original_count = 2
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify count decreased
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity_name]["participants"])
        assert new_count == original_count - 1
        assert email not in activities_response.json()[activity_name]["participants"]


class TestEdgeCases:
    """Test suite for edge cases and data validation"""
    
    def test_signup_then_remove_participant(self, client):
        """Test signing up and then removing the same participant"""
        # Arrange
        activity_name = "Art Class"
        email = "testuser@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Assert - Verify added
        get_response = client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert remove_response.status_code == 200
        
        # Assert - Verify removed
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test signing up the same user for multiple activities"""
        # Arrange
        email = "multiactivity@mergington.edu"
        activities = ["Chess Club", "Programming Class", "Art Class"]
        
        # Act - Sign up for multiple activities
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Assert - Verify in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for activity in activities:
            assert email in activities_data[activity]["participants"]
