"""
Unit Tests: Content Entity
Test the Content domain entity business logic
"""
import pytest
from datetime import datetime, timedelta

from src.core.domain.entities.content import (
    Content, Platform, ContentStatus, ContentType, ContentMetrics
)


class TestContentEntity:
    """Test Content entity business logic"""
    
    def test_content_creation_valid(self):
        """Test creating valid content"""
        content = Content(
            user_id="user-123",
            platform=Platform.TWITTER,
            text="Test social media post #test"
        )
        
        assert content.user_id == "user-123"
        assert content.platform == Platform.TWITTER
        assert content.text == "Test social media post #test"
        assert content.status == ContentStatus.DRAFT
        assert content.content_type == ContentType.POST
        assert isinstance(content.created_at, datetime)
    
    def test_content_creation_missing_user_id(self):
        """Test creating content without user ID"""
        with pytest.raises(ValueError, match="User ID is required"):
            Content(
                user_id="",
                text="Test post"
            )
    
    def test_content_creation_no_text_or_media(self):
        """Test creating content without text or media"""
        with pytest.raises(ValueError, match="Content must have text or media"):
            Content(
                user_id="user-123",
                text="",
                media_urls=[]
            )
    
    def test_content_creation_with_media_only(self):
        """Test creating content with only media"""
        content = Content(
            user_id="user-123",
            text="",
            media_urls=["https://example.com/image.jpg"]
        )
        
        assert content.text == ""
        assert len(content.media_urls) == 1
    
    def test_twitter_character_limit_validation(self):
        """Test Twitter character limit validation"""
        long_text = "x" * 281  # Exceeds 280 character limit
        
        with pytest.raises(ValueError, match="Twitter content exceeds 280 characters"):
            Content(
                user_id="user-123",
                platform=Platform.TWITTER,
                text=long_text
            )
    
    def test_twitter_character_limit_valid(self):
        """Test valid Twitter character limit"""
        text = "x" * 280  # Exactly at limit
        
        content = Content(
            user_id="user-123",
            platform=Platform.TWITTER,
            text=text
        )
        
        assert len(content.text) == 280
    
    def test_can_be_published_draft_with_text(self):
        """Test can be published for draft with text"""
        content = Content(
            user_id="user-123",
            text="Test post",
            status=ContentStatus.DRAFT
        )
        
        assert content.can_be_published() is True
    
    def test_can_be_published_scheduled(self):
        """Test can be published for scheduled content"""
        content = Content(
            user_id="user-123",
            text="Test post",
            status=ContentStatus.SCHEDULED
        )
        
        assert content.can_be_published() is True
    
    def test_can_be_published_already_published(self):
        """Test cannot republish already published content"""
        content = Content(
            user_id="user-123",
            text="Test post",
            status=ContentStatus.PUBLISHED
        )
        
        assert content.can_be_published() is False
    
    def test_can_be_published_no_content(self):
        """Test cannot publish content without text or media"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        content.text = ""  # Remove text after creation
        content.media_urls = []
        
        assert content.can_be_published() is False
    
    def test_schedule_valid(self):
        """Test valid content scheduling"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        future_time = datetime.utcnow() + timedelta(hours=1)
        initial_updated = content.updated_at
        
        content.schedule(future_time)
        
        assert content.status == ContentStatus.SCHEDULED
        assert content.scheduled_for == future_time
        assert content.updated_at > initial_updated
    
    def test_schedule_past_time(self):
        """Test scheduling with past time"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Scheduled time must be in the future"):
            content.schedule(past_time)
    
    def test_schedule_unpublishable_content(self):
        """Test scheduling unpublishable content"""
        content = Content(
            user_id="user-123",
            text="Test post",
            status=ContentStatus.PUBLISHED
        )
        future_time = datetime.utcnow() + timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Content cannot be scheduled"):
            content.schedule(future_time)
    
    def test_publish(self):
        """Test publishing content"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        initial_updated = content.updated_at
        
        content.publish("external-123", "https://platform.com/post/123")
        
        assert content.status == ContentStatus.PUBLISHED
        assert content.external_id == "external-123"
        assert content.external_url == "https://platform.com/post/123"
        assert content.published_at is not None
        assert content.updated_at > initial_updated
    
    def test_fail_publication(self):
        """Test marking publication as failed"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        initial_updated = content.updated_at
        
        content.fail_publication("API error occurred")
        
        assert content.status == ContentStatus.FAILED
        assert content.generation_parameters["error"] == "API error occurred"
        assert content.updated_at > initial_updated
    
    def test_update_metrics(self):
        """Test updating content metrics"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        
        metrics = ContentMetrics(
            impressions=1000,
            likes=50,
            shares=10,
            comments=5
        )
        initial_updated = content.updated_at
        
        content.update_metrics(metrics)
        
        assert content.metrics.impressions == 1000
        assert content.metrics.likes == 50
        assert content.metrics.engagement_rate > 0  # Should be calculated
        assert content.updated_at > initial_updated
    
    def test_add_variant(self):
        """Test adding content variant"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        initial_updated = content.updated_at
        
        content.add_variant("Alternative version of the post")
        
        assert "Alternative version of the post" in content.variants
        assert content.updated_at > initial_updated
    
    def test_add_duplicate_variant(self):
        """Test adding duplicate variant"""
        content = Content(
            user_id="user-123",
            text="Test post",
            variants=["Existing variant"]
        )
        
        content.add_variant("Existing variant")
        
        # Should not add duplicate
        assert content.variants.count("Existing variant") == 1
    
    def test_archive(self):
        """Test archiving content"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        initial_updated = content.updated_at
        
        content.archive()
        
        assert content.status == ContentStatus.ARCHIVED
        assert content.updated_at > initial_updated
    
    def test_get_character_count(self):
        """Test getting character count"""
        content = Content(
            user_id="user-123",
            text="Hello world!"
        )
        
        assert content.get_character_count() == 12
    
    def test_get_hashtag_string(self):
        """Test getting hashtag string"""
        content = Content(
            user_id="user-123",
            text="Test post",
            hashtags=["ai", "tech", "automation"]
        )
        
        hashtag_string = content.get_hashtag_string()
        assert hashtag_string == "#ai #tech #automation"
    
    def test_get_hashtag_string_empty(self):
        """Test getting hashtag string when empty"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        
        hashtag_string = content.get_hashtag_string()
        assert hashtag_string == ""
    
    def test_is_viral_true(self):
        """Test viral content detection"""
        content = Content(
            user_id="user-123",
            text="Test post",
            platform=Platform.TWITTER
        )
        
        # Set high engagement metrics
        content.metrics = ContentMetrics(
            impressions=10000,
            engagements=600  # 6% engagement rate (> 5x Twitter average of 1%)
        )
        content.metrics.engagement_rate = content.metrics.calculate_engagement_rate()
        
        assert content.is_viral() is True
    
    def test_is_viral_false(self):
        """Test non-viral content detection"""
        content = Content(
            user_id="user-123",
            text="Test post",
            platform=Platform.TWITTER
        )
        
        # Set normal engagement metrics
        content.metrics = ContentMetrics(
            impressions=1000,
            engagements=10  # 1% engagement rate (< 5x Twitter average)
        )
        content.metrics.engagement_rate = content.metrics.calculate_engagement_rate()
        
        assert content.is_viral() is False
    
    def test_is_viral_no_impressions(self):
        """Test viral detection with no impressions"""
        content = Content(
            user_id="user-123",
            text="Test post"
        )
        
        assert content.is_viral() is False
    
    def test_to_dict(self):
        """Test converting content to dictionary"""
        content = Content(
            user_id="user-123",
            platform=Platform.INSTAGRAM,
            text="Test post",
            hashtags=["test", "ai"],
            status=ContentStatus.PUBLISHED,
            external_url="https://instagram.com/p/123"
        )
        
        content_dict = content.to_dict()
        
        assert content_dict["user_id"] == "user-123"
        assert content_dict["platform"] == "instagram"
        assert content_dict["text"] == "Test post"
        assert content_dict["hashtags"] == ["test", "ai"]
        assert content_dict["status"] == "published"
        assert content_dict["external_url"] == "https://instagram.com/p/123"
        assert "created_at" in content_dict
        assert "metrics" in content_dict