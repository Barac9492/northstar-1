"""
Domain Entity: Content
Represents generated social media content
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
import uuid


class Platform(Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"


class ContentStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class ContentType(Enum):
    POST = "post"
    THREAD = "thread"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"


@dataclass
class ContentMetrics:
    """Content performance metrics"""
    impressions: int = 0
    engagements: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    clicks: int = 0
    saves: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    ctr: float = 0.0  # Click-through rate
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.impressions == 0:
            return 0.0
        return (self.engagements / self.impressions) * 100
    
    def calculate_ctr(self) -> float:
        """Calculate click-through rate"""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100


@dataclass
class Content:
    """Content domain entity"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    platform: Platform = Platform.TWITTER
    content_type: ContentType = ContentType.POST
    status: ContentStatus = ContentStatus.DRAFT
    
    # Content data
    text: str = ""
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    
    # AI generation metadata
    original_prompt: str = ""
    ai_model_used: str = ""
    generation_parameters: Dict = field(default_factory=dict)
    variants: List[str] = field(default_factory=list)
    
    # Scheduling
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # External platform data
    external_id: Optional[str] = None  # Platform-specific post ID
    external_url: Optional[str] = None
    
    # Performance
    metrics: ContentMetrics = field(default_factory=ContentMetrics)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.user_id:
            raise ValueError("User ID is required")
        
        if not self.text and not self.media_urls:
            raise ValueError("Content must have text or media")
        
        # Platform-specific validation
        if self.platform == Platform.TWITTER and len(self.text) > 280:
            raise ValueError("Twitter content exceeds 280 characters")
    
    def can_be_published(self) -> bool:
        """Business rule: Check if content can be published"""
        return (
            self.status in [ContentStatus.DRAFT, ContentStatus.SCHEDULED] and
            (self.text or self.media_urls) and
            self.platform is not None
        )
    
    def schedule(self, scheduled_time: datetime) -> None:
        """Schedule content for publishing"""
        if not self.can_be_published():
            raise ValueError("Content cannot be scheduled")
        
        if scheduled_time <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        
        self.scheduled_for = scheduled_time
        self.status = ContentStatus.SCHEDULED
        self.updated_at = datetime.utcnow()
    
    def publish(self, external_id: str, external_url: str) -> None:
        """Mark content as published"""
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.external_id = external_id
        self.external_url = external_url
        self.updated_at = datetime.utcnow()
    
    def fail_publication(self, error_message: str) -> None:
        """Mark content publication as failed"""
        self.status = ContentStatus.FAILED
        self.generation_parameters['error'] = error_message
        self.updated_at = datetime.utcnow()
    
    def update_metrics(self, metrics: ContentMetrics) -> None:
        """Update performance metrics"""
        self.metrics = metrics
        self.metrics.engagement_rate = self.metrics.calculate_engagement_rate()
        self.metrics.ctr = self.metrics.calculate_ctr()
        self.updated_at = datetime.utcnow()
    
    def add_variant(self, variant_text: str) -> None:
        """Add A/B testing variant"""
        if variant_text not in self.variants:
            self.variants.append(variant_text)
            self.updated_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Archive old content"""
        self.status = ContentStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
    
    def get_character_count(self) -> int:
        """Get character count for platform validation"""
        return len(self.text)
    
    def get_hashtag_string(self) -> str:
        """Get hashtags as a string"""
        return ' '.join(f'#{tag}' for tag in self.hashtags)
    
    def is_viral(self, threshold_multiplier: float = 5.0) -> bool:
        """Determine if content went viral based on engagement"""
        if self.metrics.impressions == 0:
            return False
        
        # Viral if engagement rate is 5x platform average
        platform_averages = {
            Platform.TWITTER: 1.0,
            Platform.INSTAGRAM: 1.5,
            Platform.LINKEDIN: 2.0,
            Platform.TIKTOK: 5.0,
            Platform.FACEBOOK: 0.8
        }
        
        average_rate = platform_averages.get(self.platform, 1.0)
        return self.metrics.engagement_rate > (average_rate * threshold_multiplier)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform.value,
            'content_type': self.content_type.value,
            'status': self.status.value,
            'text': self.text,
            'media_urls': self.media_urls,
            'hashtags': self.hashtags,
            'mentions': self.mentions,
            'original_prompt': self.original_prompt,
            'ai_model_used': self.ai_model_used,
            'generation_parameters': self.generation_parameters,
            'variants': self.variants,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'external_id': self.external_id,
            'external_url': self.external_url,
            'metrics': {
                'impressions': self.metrics.impressions,
                'engagements': self.metrics.engagements,
                'likes': self.metrics.likes,
                'shares': self.metrics.shares,
                'comments': self.metrics.comments,
                'clicks': self.metrics.clicks,
                'saves': self.metrics.saves,
                'reach': self.metrics.reach,
                'engagement_rate': self.metrics.engagement_rate,
                'ctr': self.metrics.ctr
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_viral': self.is_viral()
        }