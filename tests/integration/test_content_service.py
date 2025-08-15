"""
Integration Tests: Content Service
Test the ContentService with mock dependencies
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from src.core.application.services.content_service import ContentService
from src.core.application.dto.content_dto import CreateContentRequest
from src.core.application.exceptions import (
    UserNotFoundError, InsufficientCreditsError, 
    ValidationError, ContentGenerationError
)
from src.core.domain.entities.user import UserTier, UserStatus
from src.core.domain.entities.content import ContentStatus, Platform


class TestContentService:
    """Test ContentService integration"""
    
    @pytest.fixture
    def content_service(
        self, 
        mock_user_repository, 
        mock_content_repository,
        mock_ai_service,
        mock_social_media_service,
        mock_analytics_service
    ):
        """Create ContentService with mock dependencies"""
        return ContentService(
            user_repository=mock_user_repository,
            content_repository=mock_content_repository,
            ai_service=mock_ai_service,
            social_media_service=mock_social_media_service,
            analytics_service=mock_analytics_service
        )
    
    @pytest.mark.asyncio
    async def test_generate_content_success(self, content_service, sample_user):
        """Test successful content generation"""
        request = CreateContentRequest(
            prompt="Create a post about AI automation",
            platform="twitter",
            tone="professional",
            include_hashtags=True
        )
        
        result = await content_service.generate_content(sample_user.id, request)
        
        assert result.text == "Generated test content"
        assert result.platform == "twitter"
        assert len(result.variants) == 2
        assert len(result.hashtags) == 2
        assert result.confidence_score == 0.85
    
    @pytest.mark.asyncio
    async def test_generate_content_user_not_found(self, content_service):
        """Test content generation with non-existent user"""
        request = CreateContentRequest(
            prompt="Test prompt",
            platform="twitter"
        )
        
        with pytest.raises(UserNotFoundError):
            await content_service.generate_content("non-existent-user", request)
    
    @pytest.mark.asyncio
    async def test_generate_content_insufficient_credits(self, content_service, sample_user):
        """Test content generation with insufficient credits"""
        # Set user to free tier with max generations
        sample_user.tier = UserTier.FREE
        sample_user.monthly_generations = 10
        
        request = CreateContentRequest(
            prompt="Test prompt",
            platform="twitter"
        )
        
        with pytest.raises(InsufficientCreditsError):
            await content_service.generate_content(sample_user.id, request)
    
    @pytest.mark.asyncio
    async def test_generate_content_inactive_user(self, content_service, sample_user):
        """Test content generation with inactive user"""
        sample_user.status = UserStatus.INACTIVE
        
        request = CreateContentRequest(
            prompt="Test prompt",
            platform="twitter"
        )
        
        with pytest.raises(InsufficientCreditsError):
            await content_service.generate_content(sample_user.id, request)
    
    @pytest.mark.asyncio
    async def test_generate_content_invalid_prompt(self, content_service, sample_user):
        """Test content generation with invalid prompt"""
        request = CreateContentRequest(
            prompt="Short",  # Too short
            platform="twitter"
        )
        
        with pytest.raises(ValidationError, match="Prompt must be at least 10 characters"):
            await content_service.generate_content(sample_user.id, request)
    
    @pytest.mark.asyncio
    async def test_generate_content_invalid_platform(self, content_service, sample_user):
        """Test content generation with invalid platform"""
        with pytest.raises(ValueError):  # Pydantic validation error
            CreateContentRequest(
                prompt="This is a valid prompt for testing",
                platform="invalid_platform"
            )
    
    @pytest.mark.asyncio
    async def test_schedule_content_success(self, content_service, sample_user, sample_content):
        """Test successful content scheduling"""
        future_time = datetime.utcnow() + timedelta(hours=2)
        
        result = await content_service.schedule_content(
            sample_user.id, 
            sample_content.id, 
            future_time
        )
        
        assert result.status == ContentStatus.SCHEDULED.value
        assert result.scheduled_for == future_time
    
    @pytest.mark.asyncio
    async def test_schedule_content_user_not_found(self, content_service, sample_content):
        """Test scheduling content with non-existent user"""
        future_time = datetime.utcnow() + timedelta(hours=2)
        
        with pytest.raises(UserNotFoundError):
            await content_service.schedule_content(
                "non-existent-user", 
                sample_content.id, 
                future_time
            )
    
    @pytest.mark.asyncio
    async def test_schedule_content_not_found(self, content_service, sample_user):
        """Test scheduling non-existent content"""
        future_time = datetime.utcnow() + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="Content not found or access denied"):
            await content_service.schedule_content(
                sample_user.id, 
                "non-existent-content", 
                future_time
            )
    
    @pytest.mark.asyncio
    async def test_schedule_content_wrong_user(self, content_service, sample_user, sample_content):
        """Test scheduling content belonging to different user"""
        sample_content.user_id = "different-user"
        future_time = datetime.utcnow() + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="Content not found or access denied"):
            await content_service.schedule_content(
                sample_user.id, 
                sample_content.id, 
                future_time
            )
    
    @pytest.mark.asyncio
    async def test_publish_content_success(self, content_service, sample_user, sample_content):
        """Test successful content publishing"""
        result = await content_service.publish_content(sample_user.id, sample_content.id)
        
        assert result.status == ContentStatus.PUBLISHED.value
        assert result.external_url == "https://twitter.com/user/status/123"
    
    @pytest.mark.asyncio
    async def test_publish_content_already_published(self, content_service, sample_user, sample_content):
        """Test publishing already published content"""
        sample_content.status = ContentStatus.PUBLISHED
        
        with pytest.raises(ValidationError, match="Content cannot be published in current state"):
            await content_service.publish_content(sample_user.id, sample_content.id)
    
    @pytest.mark.asyncio
    async def test_publish_content_failed(self, content_service, sample_user, sample_content, mock_social_media_service):
        """Test failed content publishing"""
        # Make social media service raise an exception
        mock_social_media_service.publish_post = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(ContentGenerationError, match="Failed to publish content"):
            await content_service.publish_content(sample_user.id, sample_content.id)
        
        # Content should be marked as failed
        assert sample_content.status == ContentStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_get_user_content_success(self, content_service, sample_user):
        """Test getting user content"""
        result = await content_service.get_user_content(sample_user.id)
        
        assert len(result) >= 1
        assert all(content.id for content in result)
    
    @pytest.mark.asyncio
    async def test_get_user_content_with_status_filter(self, content_service, sample_user):
        """Test getting user content with status filter"""
        result = await content_service.get_user_content(
            sample_user.id, 
            status="draft"
        )
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_user_content_pagination(self, content_service, sample_user):
        """Test getting user content with pagination"""
        result = await content_service.get_user_content(
            sample_user.id, 
            limit=10, 
            offset=0
        )
        
        assert isinstance(result, list)
        assert len(result) <= 10
    
    @pytest.mark.asyncio
    async def test_get_content_analytics_success(self, content_service, sample_user, sample_content):
        """Test getting content analytics"""
        # Set content as published with external ID
        sample_content.status = ContentStatus.PUBLISHED
        sample_content.external_id = "post-123"
        
        result = await content_service.get_content_analytics(sample_user.id, sample_content.id)
        
        assert "content" in result
        assert "competitive_analysis" in result
        assert "recommendations" in result
        assert result["competitive_analysis"]["average_engagement"] == 2.0
        assert "Add more hashtags" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_get_content_analytics_draft_content(self, content_service, sample_user, sample_content):
        """Test getting analytics for draft content"""
        # Content is draft by default, no external metrics to fetch
        result = await content_service.get_content_analytics(sample_user.id, sample_content.id)
        
        assert "content" in result
        assert "competitive_analysis" in result
        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_validate_content_request_valid(self, content_service):
        """Test valid content request validation"""
        request = CreateContentRequest(
            prompt="This is a valid prompt for testing AI content generation",
            platform="twitter",
            tone="professional"
        )
        
        # Should not raise any exceptions
        content_service._validate_content_request(request)
    
    @pytest.mark.asyncio
    async def test_validate_content_request_short_prompt(self, content_service):
        """Test validation with short prompt"""
        request = CreateContentRequest(
            prompt="Short",
            platform="twitter"
        )
        
        with pytest.raises(ValidationError, match="Prompt must be at least 10 characters"):
            content_service._validate_content_request(request)
    
    @pytest.mark.asyncio
    async def test_validate_content_request_long_prompt(self, content_service):
        """Test validation with long prompt"""
        request = CreateContentRequest(
            prompt="x" * 1001,  # Exceeds 1000 character limit
            platform="twitter"
        )
        
        with pytest.raises(ValidationError, match="Prompt too long"):
            content_service._validate_content_request(request)
    
    @pytest.mark.asyncio
    async def test_validate_content_request_long_audience(self, content_service):
        """Test validation with long target audience"""
        request = CreateContentRequest(
            prompt="This is a valid prompt for testing",
            platform="twitter",
            target_audience="x" * 201  # Exceeds 200 character limit
        )
        
        with pytest.raises(ValidationError, match="Target audience description too long"):
            content_service._validate_content_request(request)