"""
Unit Tests: User Entity
Test the User domain entity business logic
"""
import pytest
from datetime import datetime

from src.core.domain.entities.user import User, UserTier, UserStatus


class TestUserEntity:
    """Test User entity business logic"""
    
    def test_user_creation_valid(self):
        """Test creating a valid user"""
        user = User(
            email="test@example.com",
            name="Test User",
            tier=UserTier.PRO
        )
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.tier == UserTier.PRO
        assert user.status == UserStatus.ACTIVE
        assert user.monthly_generations == 0
        assert user.monthly_engagements == 0
        assert isinstance(user.created_at, datetime)
    
    def test_user_creation_invalid_email(self):
        """Test creating user with invalid email"""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(email="invalid-email")
    
    def test_user_creation_missing_email(self):
        """Test creating user without email"""
        with pytest.raises(ValueError, match="Email is required"):
            User(email="")
    
    def test_can_generate_content_free_tier_within_limit(self):
        """Test content generation for free tier within limit"""
        user = User(
            email="test@example.com",
            tier=UserTier.FREE,
            monthly_generations=5
        )
        
        assert user.can_generate_content() is True
    
    def test_can_generate_content_free_tier_at_limit(self):
        """Test content generation for free tier at limit"""
        user = User(
            email="test@example.com",
            tier=UserTier.FREE,
            monthly_generations=10
        )
        
        assert user.can_generate_content() is False
    
    def test_can_generate_content_pro_tier_unlimited(self):
        """Test content generation for pro tier (unlimited)"""
        user = User(
            email="test@example.com",
            tier=UserTier.PRO,
            monthly_generations=1000
        )
        
        assert user.can_generate_content() is True
    
    def test_can_generate_content_inactive_user(self):
        """Test content generation for inactive user"""
        user = User(
            email="test@example.com",
            tier=UserTier.PRO,
            status=UserStatus.INACTIVE
        )
        
        assert user.can_generate_content() is False
    
    def test_can_auto_engage_free_tier(self):
        """Test auto-engagement for free tier (not allowed)"""
        user = User(
            email="test@example.com",
            tier=UserTier.FREE
        )
        
        assert user.can_auto_engage() is False
    
    def test_can_auto_engage_pro_tier_within_limit(self):
        """Test auto-engagement for pro tier within limit"""
        user = User(
            email="test@example.com",
            tier=UserTier.PRO,
            monthly_engagements=25
        )
        
        assert user.can_auto_engage() is True
    
    def test_can_auto_engage_pro_tier_at_limit(self):
        """Test auto-engagement for pro tier at limit"""
        user = User(
            email="test@example.com",
            tier=UserTier.PRO,
            monthly_engagements=50
        )
        
        assert user.can_auto_engage() is False
    
    def test_increment_generation_count(self):
        """Test incrementing generation count"""
        user = User(email="test@example.com")
        initial_count = user.monthly_generations
        initial_updated = user.updated_at
        
        user.increment_generation_count()
        
        assert user.monthly_generations == initial_count + 1
        assert user.last_activity is not None
        assert user.updated_at > initial_updated
    
    def test_increment_engagement_count(self):
        """Test incrementing engagement count"""
        user = User(email="test@example.com")
        initial_count = user.monthly_engagements
        initial_updated = user.updated_at
        
        user.increment_engagement_count()
        
        assert user.monthly_engagements == initial_count + 1
        assert user.last_activity is not None
        assert user.updated_at > initial_updated
    
    def test_reset_monthly_usage(self):
        """Test resetting monthly usage"""
        user = User(
            email="test@example.com",
            monthly_generations=15,
            monthly_engagements=30
        )
        initial_updated = user.updated_at
        
        user.reset_monthly_usage()
        
        assert user.monthly_generations == 0
        assert user.monthly_engagements == 0
        assert user.updated_at > initial_updated
    
    def test_upgrade_tier_valid(self):
        """Test valid tier upgrade"""
        user = User(
            email="test@example.com",
            tier=UserTier.FREE
        )
        initial_updated = user.updated_at
        
        user.upgrade_tier(UserTier.PRO)
        
        assert user.tier == UserTier.PRO
        assert user.updated_at > initial_updated
    
    def test_upgrade_tier_invalid_downgrade(self):
        """Test invalid tier downgrade"""
        user = User(
            email="test@example.com",
            tier=UserTier.PRO
        )
        
        with pytest.raises(ValueError, match="Cannot downgrade or stay same tier"):
            user.upgrade_tier(UserTier.FREE)
    
    def test_upgrade_tier_same_tier(self):
        """Test upgrading to same tier"""
        user = User(
            email="test@example.com",
            tier=UserTier.PRO
        )
        
        with pytest.raises(ValueError, match="Cannot downgrade or stay same tier"):
            user.upgrade_tier(UserTier.PRO)
    
    def test_connect_platform(self):
        """Test connecting a platform"""
        user = User(email="test@example.com")
        initial_updated = user.updated_at
        
        user.connect_platform("twitter")
        
        assert "twitter" in user.connected_platforms
        assert user.updated_at > initial_updated
    
    def test_connect_platform_already_connected(self):
        """Test connecting already connected platform"""
        user = User(
            email="test@example.com",
            connected_platforms=["twitter"]
        )
        
        user.connect_platform("twitter")
        
        # Should not add duplicate
        assert user.connected_platforms.count("twitter") == 1
    
    def test_disconnect_platform(self):
        """Test disconnecting a platform"""
        user = User(
            email="test@example.com",
            connected_platforms=["twitter", "linkedin"]
        )
        initial_updated = user.updated_at
        
        user.disconnect_platform("twitter")
        
        assert "twitter" not in user.connected_platforms
        assert "linkedin" in user.connected_platforms
        assert user.updated_at > initial_updated
    
    def test_disconnect_platform_not_connected(self):
        """Test disconnecting platform that's not connected"""
        user = User(email="test@example.com")
        
        user.disconnect_platform("twitter")
        
        # Should not raise error
        assert "twitter" not in user.connected_platforms
    
    def test_update_preferences(self):
        """Test updating user preferences"""
        user = User(
            email="test@example.com",
            preferences={"theme": "dark"}
        )
        initial_updated = user.updated_at
        
        user.update_preferences({
            "theme": "light",
            "notifications": True
        })
        
        assert user.preferences["theme"] == "light"
        assert user.preferences["notifications"] is True
        assert user.updated_at > initial_updated
    
    def test_to_dict(self):
        """Test converting user to dictionary"""
        user = User(
            email="test@example.com",
            name="Test User",
            company="Test Co",
            tier=UserTier.PRO,
            monthly_generations=5,
            connected_platforms=["twitter"]
        )
        
        user_dict = user.to_dict()
        
        assert user_dict["email"] == "test@example.com"
        assert user_dict["name"] == "Test User"
        assert user_dict["company"] == "Test Co"
        assert user_dict["tier"] == "pro"
        assert user_dict["monthly_generations"] == 5
        assert user_dict["connected_platforms"] == ["twitter"]
        assert "created_at" in user_dict
        assert "updated_at" in user_dict