"""
Domain Entity: User
Pure business logic with no external dependencies
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
import uuid


class UserTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """User domain entity with business rules"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    name: Optional[str] = None
    company: Optional[str] = None
    tier: UserTier = UserTier.FREE
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Usage tracking
    monthly_generations: int = 0
    monthly_engagements: int = 0
    last_activity: Optional[datetime] = None
    
    # Settings
    preferences: Dict = field(default_factory=dict)
    connected_platforms: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.email:
            raise ValueError("Email is required")
        
        if "@" not in self.email:
            raise ValueError("Invalid email format")
    
    def can_generate_content(self) -> bool:
        """Business rule: Check if user can generate content"""
        if self.status != UserStatus.ACTIVE:
            return False
        
        limits = {
            UserTier.FREE: 10,
            UserTier.PRO: float('inf'),
            UserTier.ENTERPRISE: float('inf')
        }
        
        return self.monthly_generations < limits[self.tier]
    
    def can_auto_engage(self) -> bool:
        """Business rule: Check if user can use auto-engagement"""
        if self.status != UserStatus.ACTIVE:
            return False
        
        limits = {
            UserTier.FREE: 0,  # No auto-engagement for free tier
            UserTier.PRO: 50,
            UserTier.ENTERPRISE: float('inf')
        }
        
        return self.monthly_engagements < limits[self.tier]
    
    def increment_generation_count(self) -> None:
        """Track content generation usage"""
        self.monthly_generations += 1
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_engagement_count(self) -> None:
        """Track engagement usage"""
        self.monthly_engagements += 1
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def reset_monthly_usage(self) -> None:
        """Reset monthly counters (called by scheduled job)"""
        self.monthly_generations = 0
        self.monthly_engagements = 0
        self.updated_at = datetime.utcnow()
    
    def upgrade_tier(self, new_tier: UserTier) -> None:
        """Business rule: Upgrade user tier"""
        tier_hierarchy = {
            UserTier.FREE: 0,
            UserTier.PRO: 1,
            UserTier.ENTERPRISE: 2
        }
        
        if tier_hierarchy[new_tier] <= tier_hierarchy[self.tier]:
            raise ValueError("Cannot downgrade or stay same tier")
        
        self.tier = new_tier
        self.updated_at = datetime.utcnow()
    
    def connect_platform(self, platform: str) -> None:
        """Connect a social media platform"""
        if platform not in self.connected_platforms:
            self.connected_platforms.append(platform)
            self.updated_at = datetime.utcnow()
    
    def disconnect_platform(self, platform: str) -> None:
        """Disconnect a social media platform"""
        if platform in self.connected_platforms:
            self.connected_platforms.remove(platform)
            self.updated_at = datetime.utcnow()
    
    def update_preferences(self, preferences: Dict) -> None:
        """Update user preferences"""
        self.preferences.update(preferences)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'tier': self.tier.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'monthly_generations': self.monthly_generations,
            'monthly_engagements': self.monthly_engagements,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'preferences': self.preferences,
            'connected_platforms': self.connected_platforms
        }