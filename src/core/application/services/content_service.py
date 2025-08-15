"""
Application Service: Content Service
Orchestrates business logic for content management
"""
from typing import Optional, List, Dict
from datetime import datetime
import logging

from ..interfaces.ai_service import AIService
from ..interfaces.social_media_service import SocialMediaService
from ..interfaces.analytics_service import AnalyticsService
from ...domain.entities.user import User
from ...domain.entities.content import Content, Platform, ContentStatus
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.content_repository import ContentRepository
from ..dto.content_dto import CreateContentRequest, ContentResponse
from ..exceptions import (
    UserNotFoundError, 
    InsufficientCreditsError, 
    ContentGenerationError,
    ValidationError
)

logger = logging.getLogger(__name__)


class ContentService:
    """Content service for managing AI-generated content"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        content_repository: ContentRepository,
        ai_service: AIService,
        social_media_service: SocialMediaService,
        analytics_service: AnalyticsService
    ):
        self._user_repo = user_repository
        self._content_repo = content_repository
        self._ai_service = ai_service
        self._social_media_service = social_media_service
        self._analytics_service = analytics_service
    
    async def generate_content(
        self, 
        user_id: str, 
        request: CreateContentRequest
    ) -> ContentResponse:
        """Generate AI-powered social media content"""
        
        # 1. Validate user and permissions
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        if not user.can_generate_content():
            raise InsufficientCreditsError(
                "Monthly generation limit reached. Upgrade your plan."
            )
        
        # 2. Validate request
        self._validate_content_request(request)
        
        try:
            # 3. Generate content using AI
            logger.info(f"Generating content for user {user_id}, platform {request.platform}")
            
            ai_result = await self._ai_service.generate_content(
                platform=request.platform,
                prompt=request.prompt,
                tone=request.tone,
                include_hashtags=request.include_hashtags,
                include_emojis=request.include_emojis,
                target_audience=request.target_audience
            )
            
            # 4. Create content entity
            content = Content(
                user_id=user_id,
                platform=Platform(request.platform),
                text=ai_result.primary_content,
                original_prompt=request.prompt,
                ai_model_used=ai_result.model_used,
                generation_parameters={
                    'tone': request.tone,
                    'include_hashtags': request.include_hashtags,
                    'include_emojis': request.include_emojis,
                    'target_audience': request.target_audience,
                    'confidence_score': ai_result.confidence_score
                },
                variants=ai_result.variants,
                hashtags=ai_result.hashtags,
                status=ContentStatus.DRAFT
            )
            
            # 5. Save content
            saved_content = await self._content_repo.create(content)
            
            # 6. Update user usage
            user.increment_generation_count()
            await self._user_repo.update(user)
            
            # 7. Get performance prediction
            prediction = await self._analytics_service.predict_performance(saved_content)
            
            logger.info(f"Content generated successfully: {saved_content.id}")
            
            return ContentResponse(
                id=saved_content.id,
                text=saved_content.text,
                platform=saved_content.platform.value,
                variants=saved_content.variants,
                hashtags=saved_content.hashtags,
                predicted_engagement_rate=prediction.engagement_rate,
                predicted_reach=prediction.reach,
                confidence_score=ai_result.confidence_score,
                created_at=saved_content.created_at
            )
            
        except Exception as e:
            logger.error(f"Content generation failed for user {user_id}: {str(e)}")
            raise ContentGenerationError(f"Failed to generate content: {str(e)}")
    
    async def schedule_content(
        self, 
        user_id: str, 
        content_id: str, 
        scheduled_time: datetime
    ) -> ContentResponse:
        """Schedule content for publishing"""
        
        # 1. Validate user
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # 2. Get content
        content = await self._content_repo.get_by_id(content_id)
        if not content or content.user_id != user_id:
            raise ValidationError("Content not found or access denied")
        
        # 3. Schedule content
        content.schedule(scheduled_time)
        
        # 4. Save updated content
        updated_content = await self._content_repo.update(content)
        
        # 5. Register with scheduler
        await self._social_media_service.schedule_post(
            content=updated_content,
            scheduled_time=scheduled_time
        )
        
        logger.info(f"Content {content_id} scheduled for {scheduled_time}")
        
        return ContentResponse.from_entity(updated_content)
    
    async def publish_content(
        self, 
        user_id: str, 
        content_id: str
    ) -> ContentResponse:
        """Publish content immediately"""
        
        # 1. Validate user
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # 2. Get content
        content = await self._content_repo.get_by_id(content_id)
        if not content or content.user_id != user_id:
            raise ValidationError("Content not found or access denied")
        
        # 3. Validate content can be published
        if not content.can_be_published():
            raise ValidationError("Content cannot be published in current state")
        
        try:
            # 4. Publish to social media platform
            result = await self._social_media_service.publish_post(content)
            
            # 5. Update content with publication details
            content.publish(
                external_id=result.post_id,
                external_url=result.post_url
            )
            
            # 6. Save updated content
            updated_content = await self._content_repo.update(content)
            
            logger.info(f"Content {content_id} published successfully")
            
            return ContentResponse.from_entity(updated_content)
            
        except Exception as e:
            # Mark as failed
            content.fail_publication(str(e))
            await self._content_repo.update(content)
            
            logger.error(f"Failed to publish content {content_id}: {str(e)}")
            raise ContentGenerationError(f"Failed to publish content: {str(e)}")
    
    async def get_user_content(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[ContentResponse]:
        """Get user's content with pagination"""
        
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        content_status = ContentStatus(status) if status else None
        content_list = await self._content_repo.list_by_user(
            user_id=user_id,
            status=content_status,
            limit=limit,
            offset=offset
        )
        
        return [ContentResponse.from_entity(content) for content in content_list]
    
    async def get_content_analytics(
        self, 
        user_id: str, 
        content_id: str
    ) -> Dict:
        """Get detailed analytics for specific content"""
        
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        content = await self._content_repo.get_by_id(content_id)
        if not content or content.user_id != user_id:
            raise ValidationError("Content not found or access denied")
        
        # Get latest metrics from social media platform
        if content.status == ContentStatus.PUBLISHED and content.external_id:
            fresh_metrics = await self._social_media_service.get_post_metrics(
                platform=content.platform,
                post_id=content.external_id
            )
            
            if fresh_metrics:
                content.update_metrics(fresh_metrics)
                await self._content_repo.update(content)
        
        # Get competitive analysis
        competitive_data = await self._analytics_service.get_competitive_analysis(
            platform=content.platform,
            content_type=content.content_type
        )
        
        return {
            'content': content.to_dict(),
            'competitive_analysis': competitive_data,
            'recommendations': await self._analytics_service.get_optimization_recommendations(content)
        }
    
    def _validate_content_request(self, request: CreateContentRequest) -> None:
        """Validate content generation request"""
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise ValidationError("Prompt must be at least 10 characters")
        
        if len(request.prompt) > 1000:
            raise ValidationError("Prompt too long (max 1000 characters)")
        
        valid_platforms = [p.value for p in Platform]
        if request.platform not in valid_platforms:
            raise ValidationError(f"Invalid platform. Must be one of: {valid_platforms}")
        
        if request.target_audience and len(request.target_audience) > 200:
            raise ValidationError("Target audience description too long (max 200 characters)")