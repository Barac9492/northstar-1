"""
Data Transfer Objects for Content Operations
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime


class CreateContentRequest(BaseModel):
    """Request model for content generation"""
    prompt: str = Field(..., min_length=10, max_length=1000, description="Content generation prompt")
    platform: str = Field(..., description="Target social media platform")
    tone: Optional[str] = Field(None, description="Content tone (professional, casual, friendly, etc.)")
    target_audience: Optional[str] = Field(None, max_length=200, description="Target audience description")
    include_hashtags: bool = Field(True, description="Include relevant hashtags")
    include_emojis: bool = Field(True, description="Include relevant emojis")
    
    @validator('platform')
    def validate_platform(cls, v):
        valid_platforms = ['twitter', 'instagram', 'linkedin', 'tiktok', 'facebook']
        if v.lower() not in valid_platforms:
            raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v.lower()
    
    @validator('tone')
    def validate_tone(cls, v):
        if v is not None:
            valid_tones = ['professional', 'casual', 'friendly', 'humorous', 'formal', 'creative']
            if v.lower() not in valid_tones:
                raise ValueError(f'Tone must be one of: {valid_tones}')
            return v.lower()
        return v


class ContentResponse(BaseModel):
    """Response model for content operations"""
    id: str
    text: str
    platform: str
    variants: List[str] = []
    hashtags: List[str] = []
    predicted_engagement_rate: Optional[float] = None
    predicted_reach: Optional[int] = None
    confidence_score: Optional[float] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    external_url: Optional[str] = None
    metrics: Optional[Dict] = None
    created_at: datetime
    
    @classmethod
    def from_entity(cls, content):
        """Create response from Content entity"""
        return cls(
            id=content.id,
            text=content.text,
            platform=content.platform.value,
            variants=content.variants,
            hashtags=content.hashtags,
            status=content.status.value,
            scheduled_for=content.scheduled_for,
            published_at=content.published_at,
            external_url=content.external_url,
            metrics={
                'impressions': content.metrics.impressions,
                'engagements': content.metrics.engagements,
                'likes': content.metrics.likes,
                'shares': content.metrics.shares,
                'comments': content.metrics.comments,
                'engagement_rate': content.metrics.engagement_rate
            } if content.metrics else None,
            created_at=content.created_at
        )


class ScheduleContentRequest(BaseModel):
    """Request model for scheduling content"""
    scheduled_time: datetime = Field(..., description="When to publish the content")
    
    @validator('scheduled_time')
    def validate_future_time(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v


class ContentAnalyticsResponse(BaseModel):
    """Response model for content analytics"""
    content_id: str
    metrics: Dict
    competitive_analysis: Dict
    recommendations: List[str]
    performance_score: Optional[float] = None