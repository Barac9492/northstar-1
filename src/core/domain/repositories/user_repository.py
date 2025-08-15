"""
Repository Interface: User Repository
Defines the contract for user data access without implementation details
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from ..entities.user import User, UserTier, UserStatus


class UserRepository(ABC):
    """Abstract repository for user data access"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        pass
    
    @abstractmethod
    async def list_by_tier(self, tier: UserTier, limit: int = 100, offset: int = 0) -> List[User]:
        """Get users by tier with pagination"""
        pass
    
    @abstractmethod
    async def list_by_status(self, status: UserStatus, limit: int = 100, offset: int = 0) -> List[User]:
        """Get users by status with pagination"""
        pass
    
    @abstractmethod
    async def count_by_tier(self, tier: UserTier) -> int:
        """Count users by tier"""
        pass
    
    @abstractmethod
    async def get_usage_stats(self, user_id: str) -> Dict:
        """Get user usage statistics"""
        pass
    
    @abstractmethod
    async def reset_monthly_usage(self, user_ids: List[str]) -> int:
        """Reset monthly usage for multiple users"""
        pass
    
    @abstractmethod
    async def find_inactive_users(self, days: int) -> List[User]:
        """Find users inactive for specified days"""
        pass
    
    @abstractmethod
    async def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by email, name, or company"""
        pass