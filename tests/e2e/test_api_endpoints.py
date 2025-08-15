"""
End-to-End Tests: API Endpoints
Test the complete API flow from request to response
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from src.api.main import app


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


class TestContentAPI:
    """Test content API endpoints"""
    
    def test_generate_content_success(self, client, auth_headers):
        """Test successful content generation"""
        payload = {
            "prompt": "Create an engaging post about AI automation in business",
            "platform": "twitter",
            "tone": "professional",
            "include_hashtags": True,
            "include_emojis": False
        }
        
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            # Mock the content service
            mock_service = mock_resolve.return_value
            mock_service.generate_content.return_value = {
                "id": "content-123",
                "text": "AI automation is revolutionizing business processes! #AI #automation",
                "platform": "twitter",
                "variants": ["Alternative version"],
                "hashtags": ["AI", "automation"],
                "confidence_score": 0.85,
                "created_at": "2024-01-01T12:00:00"
            }
            
            response = client.post(
                "/content/generate",
                json=payload,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "AI automation is revolutionizing business processes! #AI #automation"
        assert data["platform"] == "twitter"
        assert "AI" in data["hashtags"]
    
    def test_generate_content_invalid_prompt(self, client, auth_headers):
        """Test content generation with invalid prompt"""
        payload = {
            "prompt": "Short",  # Too short
            "platform": "twitter"
        }
        
        response = client.post(
            "/content/generate",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "validation_errors" in data["error"]["details"]
    
    def test_generate_content_invalid_platform(self, client, auth_headers):
        """Test content generation with invalid platform"""
        payload = {
            "prompt": "This is a valid prompt for testing",
            "platform": "invalid_platform"
        }
        
        response = client.post(
            "/content/generate",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_content_unauthorized(self, client):
        """Test content generation without authentication"""
        payload = {
            "prompt": "This is a valid prompt for testing",
            "platform": "twitter"
        }
        
        response = client.post("/content/generate", json=payload)
        
        assert response.status_code == 401
    
    def test_generate_content_rate_limited(self, client, auth_headers):
        """Test content generation rate limiting"""
        payload = {
            "prompt": "This is a valid prompt for testing",
            "platform": "twitter"
        }
        
        # Simulate rate limit exceeded
        with patch('src.api.middleware.rate_limiting.rate_limiter.is_allowed') as mock_rate_limit:
            mock_rate_limit.return_value = (False, {
                'limit': 100,
                'remaining': 0,
                'reset': 1640995200,
                'retry_after': 3600
            })
            
            response = client.post(
                "/content/generate",
                json=payload,
                headers=auth_headers
            )
        
        assert response.status_code == 429
        assert "X-RateLimit-Limit" in response.headers
    
    def test_schedule_content_success(self, client, auth_headers):
        """Test successful content scheduling"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.schedule_content.return_value = {
                "id": "content-123",
                "status": "scheduled",
                "scheduled_for": "2024-01-02T12:00:00",
                "text": "Test content"
            }
            
            response = client.post(
                "/content/content-123/schedule",
                json={"scheduled_time": "2024-01-02T12:00:00"},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "scheduled"
    
    def test_publish_content_success(self, client, auth_headers):
        """Test successful content publishing"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.publish_content.return_value = {
                "id": "content-123",
                "status": "published",
                "external_url": "https://twitter.com/user/status/123",
                "text": "Published content"
            }
            
            response = client.post(
                "/content/content-123/publish",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert "external_url" in data
    
    def test_get_user_content_success(self, client, auth_headers):
        """Test getting user content"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.get_user_content.return_value = [
                {
                    "id": "content-1",
                    "text": "First post",
                    "platform": "twitter",
                    "status": "published"
                },
                {
                    "id": "content-2", 
                    "text": "Second post",
                    "platform": "instagram",
                    "status": "draft"
                }
            ]
            
            response = client.get("/content/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "content-1"
    
    def test_get_user_content_with_pagination(self, client, auth_headers):
        """Test getting user content with pagination"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.get_user_content.return_value = []
            
            response = client.get(
                "/content/?limit=10&offset=20&status=published",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        # Verify the service was called with correct parameters
        mock_service.get_user_content.assert_called_once_with(
            "test-user-123", 10, 20, "published"
        )
    
    def test_get_content_by_id_success(self, client, auth_headers):
        """Test getting specific content by ID"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.get_user_content.return_value = [
                {
                    "id": "content-123",
                    "text": "Specific content",
                    "platform": "twitter",
                    "status": "published"
                }
            ]
            
            response = client.get("/content/content-123", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "content-123"
    
    def test_get_content_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent content"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.get_user_content.return_value = []  # No content found
            
            response = client.get("/content/non-existent", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_content_analytics_success(self, client, auth_headers):
        """Test getting content analytics"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.get_content_analytics.return_value = {
                "content": {"id": "content-123"},
                "competitive_analysis": {"average_engagement": 2.5},
                "recommendations": ["Add more hashtags"]
            }
            
            response = client.get("/content/content-123/analytics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "competitive_analysis" in data
        assert "recommendations" in data
    
    def test_delete_content_success(self, client, auth_headers):
        """Test successful content deletion"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_repo = mock_resolve.return_value
            mock_content = type('MockContent', (), {
                'user_id': 'test-user-123'
            })()
            mock_repo.get_by_id.return_value = mock_content
            mock_repo.delete.return_value = True
            
            response = client.delete("/content/content-123", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Content deleted successfully"
    
    def test_delete_content_not_found(self, client, auth_headers):
        """Test deleting non-existent content"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_repo = mock_resolve.return_value
            mock_repo.get_by_id.return_value = None
            
            response = client.delete("/content/non-existent", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_content_wrong_user(self, client, auth_headers):
        """Test deleting content belonging to different user"""
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_repo = mock_resolve.return_value
            mock_content = type('MockContent', (), {
                'user_id': 'different-user'
            })()
            mock_repo.get_by_id.return_value = mock_content
            
            response = client.delete("/content/content-123", headers=auth_headers)
        
        assert response.status_code == 404


class TestHealthEndpoints:
    """Test health and monitoring endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        
        # Should be accessible without authentication
        assert response.status_code in [200, 404]  # 404 if not implemented yet


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_json(self, client, auth_headers):
        """Test handling of invalid JSON"""
        response = client.post(
            "/content/generate",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client, auth_headers):
        """Test handling of missing required fields"""
        payload = {
            "platform": "twitter"
            # Missing required 'prompt' field
        }
        
        response = client.post(
            "/content/generate",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
    
    def test_internal_server_error(self, client, auth_headers):
        """Test handling of internal server errors"""
        payload = {
            "prompt": "This is a valid prompt for testing",
            "platform": "twitter"
        }
        
        with patch('src.infrastructure.di.container.container.resolve') as mock_resolve:
            mock_service = mock_resolve.return_value
            mock_service.generate_content.side_effect = Exception("Database error")
            
            response = client.post(
                "/content/generate",
                json=payload,
                headers=auth_headers
            )
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "request_id" in data["error"]