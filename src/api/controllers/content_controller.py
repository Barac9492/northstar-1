"""
API Controller: Content Management
FastAPI controller for content-related endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..middleware.auth import get_current_user
from ..middleware.rate_limiting import rate_limit
from ...core.application.services.content_service import ContentService
from ...core.application.dto.content_dto import CreateContentRequest, ContentResponse
from ...core.application.exceptions import (
    UserNotFoundError,
    InsufficientCreditsError,
    ContentGenerationError,
    ValidationError
)
from ...infrastructure.di.container import container

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/generate", response_model=ContentResponse)
@rate_limit("content_generation", per_hour=100)
async def generate_content(
    request: CreateContentRequest,
    user_id: str = Depends(get_current_user)
):
    """Generate AI-powered social media content"""
    try:
        content_service = container.resolve(ContentService)
        return await content_service.generate_content(user_id, request)
    
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientCreditsError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{content_id}/schedule", response_model=ContentResponse)
async def schedule_content(
    content_id: str,
    scheduled_time: datetime,
    user_id: str = Depends(get_current_user)
):
    """Schedule content for publishing"""
    try:
        content_service = container.resolve(ContentService)
        return await content_service.schedule_content(user_id, content_id, scheduled_time)
    
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Publish content immediately"""
    try:
        content_service = container.resolve(ContentService)
        return await content_service.publish_content(user_id, content_id)
    
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ContentResponse])
async def get_user_content(
    user_id: str = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None)
):
    """Get user's content with pagination"""
    try:
        content_service = container.resolve(ContentService)
        return await content_service.get_user_content(user_id, limit, offset, status)
    
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get specific content by ID"""
    try:
        content_service = container.resolve(ContentService)
        content_list = await content_service.get_user_content(user_id, limit=1000)
        
        for content in content_list:
            if content.id == content_id:
                return content
        
        raise HTTPException(status_code=404, detail="Content not found")
    
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{content_id}/analytics")
async def get_content_analytics(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get detailed analytics for specific content"""
    try:
        content_service = container.resolve(ContentService)
        return await content_service.get_content_analytics(user_id, content_id)
    
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete content"""
    try:
        from ...core.domain.repositories.content_repository import ContentRepository
        content_repo = container.resolve(ContentRepository)
        
        # Verify ownership
        content = await content_repo.get_by_id(content_id)
        if not content or content.user_id != user_id:
            raise HTTPException(status_code=404, detail="Content not found")
        
        success = await content_repo.delete(content_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete content")
        
        return {"message": "Content deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))