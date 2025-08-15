"""
Repository Interface: Content Repository
Defines the contract for content data access without implementation details
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.content import Content, Platform, ContentStatus


class ContentRepository(ABC):
    """Abstract repository for content data access"""
    
    @abstractmethod
    async def create(self, content: Content) -> Content:
        """Create new content"""
        pass
    
    @abstractmethod
    async def get_by_id(self, content_id: str) -> Optional[Content]:
        """Get content by ID"""
        pass
    
    @abstractmethod
    async def update(self, content: Content) -> Content:
        """Update existing content"""
        pass
    
    @abstractmethod
    async def delete(self, content_id: str) -> bool:
        """Delete content by ID"""
        pass
    
    @abstractmethod
    async def list_by_user(
        self, 
        user_id: str, 
        status: Optional[ContentStatus] = None,
        limit: int = 50, 
        offset: int = 0
    ) -> List[Content]:
        """Get content by user with optional status filter"""
        pass
    
    @abstractmethod
    async def list_by_platform(
        self, 
        platform: Platform, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Content]:
        """Get content by platform"""
        pass
    
    @abstractmethod
    async def list_scheduled_content(self, limit: int = 100) -> List[Content]:
        """Get content scheduled for publishing"""
        pass
    
    @abstractmethod
    async def get_analytics_summary(self, user_id: str, days: int = 30) -> dict:
        """Get analytics summary for user"""
        pass
    
    @abstractmethod
    async def get_top_performing_content(
        self, 
        user_id: str, 
        metric: str = 'engagement_rate',
        limit: int = 10
    ) -> List[Content]:
        """Get top performing content by metric"""
        pass
    
    @abstractmethod
    async def search_content(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 50
    ) -> List[Content]:
        """Search content by text"""
        pass