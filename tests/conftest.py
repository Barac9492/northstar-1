"""
Test Configuration
Pytest fixtures and configuration for testing
"""
import pytest
import asyncio
import asyncpg
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.core.domain.entities.user import User, UserTier, UserStatus
from src.core.domain.entities.content import Content, Platform, ContentStatus
from src.infrastructure.config.settings import Settings, Environment
from src.infrastructure.di.container import Container


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Test settings configuration"""
    # Override environment for testing
    import os
    os.environ["ENVIRONMENT"] = "testing"
    
    settings = Settings()
    settings.database.name = "northstar_test"
    settings.redis.db = 1  # Use different Redis DB for tests
    
    return settings


@pytest.fixture
def container() -> Container:
    """Test dependency injection container"""
    return Container()


@pytest.fixture
def mock_db_pool():
    """Mock database connection pool"""
    pool = AsyncMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    pool.acquire.return_value.__aexit__.return_value = None
    return pool


@pytest.fixture
def sample_user() -> User:
    """Sample user for testing"""
    return User(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
        company="Test Company",
        tier=UserTier.PRO,
        status=UserStatus.ACTIVE,
        monthly_generations=5,
        monthly_engagements=10,
        created_at=datetime.utcnow(),
        preferences={
            "default_tone": "professional",
            "include_hashtags": True
        },
        connected_platforms=["twitter", "linkedin"]
    )


@pytest.fixture
def sample_content(sample_user: User) -> Content:
    """Sample content for testing"""
    return Content(
        id="test-content-123",
        user_id=sample_user.id,
        platform=Platform.TWITTER,
        text="This is a test social media post about AI and automation! #AI #tech",
        original_prompt="Create a post about AI",
        ai_model_used="claude-3-5-sonnet-20241022",
        hashtags=["AI", "tech"],
        status=ContentStatus.DRAFT,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client"""
    client = Mock()
    
    # Mock successful response
    mock_response = Mock()
    mock_response.content = [Mock(text="Generated social media content!")]
    
    client.messages.create.return_value = mock_response
    return client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    client = AsyncMock()
    
    # Mock Redis operations
    client.get.return_value = None
    client.set.return_value = True
    client.delete.return_value = 1
    client.expire.return_value = True
    client.zcard.return_value = 0
    client.zadd.return_value = 1
    client.zremrangebyscore.return_value = 0
    
    return client


class MockUserRepository:
    """Mock user repository for testing"""
    
    def __init__(self):
        self.users = {}
    
    async def create(self, user: User) -> User:
        self.users[user.id] = user
        return user
    
    async def get_by_id(self, user_id: str) -> User:
        return self.users.get(user_id)
    
    async def get_by_email(self, email: str) -> User:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    async def update(self, user: User) -> User:
        self.users[user.id] = user
        return user
    
    async def delete(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


class MockContentRepository:
    """Mock content repository for testing"""
    
    def __init__(self):
        self.content = {}
    
    async def create(self, content: Content) -> Content:
        self.content[content.id] = content
        return content
    
    async def get_by_id(self, content_id: str) -> Content:
        return self.content.get(content_id)
    
    async def update(self, content: Content) -> Content:
        self.content[content.id] = content
        return content
    
    async def delete(self, content_id: str) -> bool:
        if content_id in self.content:
            del self.content[content_id]
            return True
        return False
    
    async def list_by_user(self, user_id: str, status=None, limit=50, offset=0):
        user_content = [c for c in self.content.values() if c.user_id == user_id]
        if status:
            user_content = [c for c in user_content if c.status == status]
        return user_content[offset:offset + limit]


@pytest.fixture
def mock_user_repository():
    """Mock user repository fixture"""
    return MockUserRepository()


@pytest.fixture
def mock_content_repository():
    """Mock content repository fixture"""
    return MockContentRepository()


class MockAIService:
    """Mock AI service for testing"""
    
    async def generate_content(self, **kwargs):
        return Mock(
            primary_content="Generated test content",
            variants=["Variant 1", "Variant 2"],
            hashtags=["test", "ai"],
            confidence_score=0.85,
            model_used="claude-3-5-sonnet-20241022"
        )


class MockSocialMediaService:
    """Mock social media service for testing"""
    
    async def publish_post(self, content):
        return Mock(
            post_id="mock-post-123",
            post_url="https://twitter.com/user/status/123"
        )
    
    async def schedule_post(self, content, scheduled_time):
        return True
    
    async def get_post_metrics(self, platform, post_id):
        return Mock(
            impressions=1000,
            likes=50,
            shares=10,
            comments=5
        )


class MockAnalyticsService:
    """Mock analytics service for testing"""
    
    async def predict_performance(self, content):
        return Mock(
            engagement_rate=2.5,
            reach=1000
        )
    
    async def get_competitive_analysis(self, platform, content_type):
        return {
            "average_engagement": 2.0,
            "top_hashtags": ["trending", "popular"]
        }
    
    async def get_optimization_recommendations(self, content):
        return [
            "Add more hashtags",
            "Post at optimal time"
        ]


@pytest.fixture
def mock_ai_service():
    """Mock AI service fixture"""
    return MockAIService()


@pytest.fixture
def mock_social_media_service():
    """Mock social media service fixture"""
    return MockSocialMediaService()


@pytest.fixture
def mock_analytics_service():
    """Mock analytics service fixture"""
    return MockAnalyticsService()


@pytest.fixture
async def db_transaction():
    """Database transaction for testing (rollback after test)"""
    # This would be used for integration tests with a real database
    # For now, we'll just return a mock
    yield None


@pytest.fixture
def jwt_token():
    """Valid JWT token for testing"""
    from src.api.middleware.auth import jwt_manager
    return jwt_manager.create_access_token("test-user-123")


@pytest.fixture
def auth_headers(jwt_token):
    """Authorization headers for testing"""
    return {"Authorization": f"Bearer {jwt_token}"}


@pytest.fixture(autouse=True)
async def setup_test_data(mock_user_repository, mock_content_repository, sample_user, sample_content):
    """Setup test data before each test"""
    await mock_user_repository.create(sample_user)
    await mock_content_repository.create(sample_content)