"""
PostgreSQL Implementation of Content Repository
Concrete implementation of the content repository interface
"""
from typing import Optional, List
import asyncpg
import json
from datetime import datetime

from ....core.domain.entities.content import Content, Platform, ContentStatus, ContentType, ContentMetrics
from ....core.domain.repositories.content_repository import ContentRepository
from ...di.container import service


@service(ContentRepository, 'singleton')
class PostgreSQLContentRepository(ContentRepository):
    """PostgreSQL implementation of content repository"""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def create(self, content: Content) -> Content:
        """Create new content"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO content (
                    id, user_id, platform, content_type, status,
                    text, media_urls, hashtags, mentions,
                    original_prompt, ai_model_used, generation_parameters, variants,
                    scheduled_for, published_at, external_id, external_url,
                    metrics, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
            """,
                content.id, content.user_id, content.platform.value, 
                content.content_type.value, content.status.value,
                content.text, json.dumps(content.media_urls), 
                json.dumps(content.hashtags), json.dumps(content.mentions),
                content.original_prompt, content.ai_model_used, 
                json.dumps(content.generation_parameters), json.dumps(content.variants),
                content.scheduled_for, content.published_at, 
                content.external_id, content.external_url,
                self._metrics_to_json(content.metrics), 
                content.created_at, content.updated_at
            )
            
            return content
    
    async def get_by_id(self, content_id: str) -> Optional[Content]:
        """Get content by ID"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM content WHERE id = $1", content_id
            )
            
            if not row:
                return None
            
            return self._row_to_content(row)
    
    async def update(self, content: Content) -> Content:
        """Update existing content"""
        content.updated_at = datetime.utcnow()
        
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE content SET 
                    platform = $2, content_type = $3, status = $4,
                    text = $5, media_urls = $6, hashtags = $7, mentions = $8,
                    original_prompt = $9, ai_model_used = $10, 
                    generation_parameters = $11, variants = $12,
                    scheduled_for = $13, published_at = $14, 
                    external_id = $15, external_url = $16,
                    metrics = $17, updated_at = $18
                WHERE id = $1
            """,
                content.id, content.platform.value, content.content_type.value, 
                content.status.value, content.text, json.dumps(content.media_urls),
                json.dumps(content.hashtags), json.dumps(content.mentions),
                content.original_prompt, content.ai_model_used,
                json.dumps(content.generation_parameters), json.dumps(content.variants),
                content.scheduled_for, content.published_at,
                content.external_id, content.external_url,
                self._metrics_to_json(content.metrics), content.updated_at
            )
            
            return content
    
    async def delete(self, content_id: str) -> bool:
        """Delete content by ID"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM content WHERE id = $1", content_id
            )
            
            return result == "DELETE 1"
    
    async def list_by_user(
        self, 
        user_id: str, 
        status: Optional[ContentStatus] = None,
        limit: int = 50, 
        offset: int = 0
    ) -> List[Content]:
        """Get content by user with optional status filter"""
        query = "SELECT * FROM content WHERE user_id = $1"
        params = [user_id]
        
        if status:
            query += " AND status = $2"
            params.append(status.value)
            query += " ORDER BY created_at DESC LIMIT $3 OFFSET $4"
            params.extend([limit, offset])
        else:
            query += " ORDER BY created_at DESC LIMIT $2 OFFSET $3"
            params.extend([limit, offset])
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_content(row) for row in rows]
    
    async def list_by_platform(
        self, 
        platform: Platform, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Content]:
        """Get content by platform"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM content 
                WHERE platform = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
            """, platform.value, limit, offset)
            
            return [self._row_to_content(row) for row in rows]
    
    async def list_scheduled_content(self, limit: int = 100) -> List[Content]:
        """Get content scheduled for publishing"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM content 
                WHERE status = 'scheduled' 
                AND scheduled_for <= NOW() 
                ORDER BY scheduled_for ASC 
                LIMIT $1
            """, limit)
            
            return [self._row_to_content(row) for row in rows]
    
    async def get_analytics_summary(self, user_id: str, days: int = 30) -> dict:
        """Get analytics summary for user"""
        async with self.db_pool.acquire() as conn:
            # Get basic stats
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_content,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published_count,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_count,
                    COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_count
                FROM content 
                WHERE user_id = $1 
                AND created_at >= NOW() - INTERVAL '%s days'
            """ % days, user_id)
            
            # Get platform breakdown
            platform_stats = await conn.fetch("""
                SELECT 
                    platform,
                    COUNT(*) as count,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published
                FROM content 
                WHERE user_id = $1 
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY platform
            """ % days, user_id)
            
            # Get engagement metrics for published content
            engagement_stats = await conn.fetchrow("""
                SELECT 
                    COALESCE(AVG((metrics->>'engagement_rate')::float), 0) as avg_engagement_rate,
                    COALESCE(SUM((metrics->>'impressions')::int), 0) as total_impressions,
                    COALESCE(SUM((metrics->>'likes')::int), 0) as total_likes,
                    COALESCE(SUM((metrics->>'shares')::int), 0) as total_shares
                FROM content 
                WHERE user_id = $1 
                AND status = 'published'
                AND created_at >= NOW() - INTERVAL '%s days'
            """ % days, user_id)
            
            return {
                'total_content': stats['total_content'],
                'published_count': stats['published_count'],
                'scheduled_count': stats['scheduled_count'],
                'draft_count': stats['draft_count'],
                'platform_breakdown': [
                    {
                        'platform': row['platform'],
                        'total': row['count'],
                        'published': row['published']
                    } for row in platform_stats
                ],
                'engagement': {
                    'avg_engagement_rate': float(engagement_stats['avg_engagement_rate']),
                    'total_impressions': engagement_stats['total_impressions'],
                    'total_likes': engagement_stats['total_likes'],
                    'total_shares': engagement_stats['total_shares']
                }
            }
    
    async def get_top_performing_content(
        self, 
        user_id: str, 
        metric: str = 'engagement_rate',
        limit: int = 10
    ) -> List[Content]:
        """Get top performing content by metric"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT * FROM content 
                WHERE user_id = $1 
                AND status = 'published'
                AND (metrics->>'{metric}')::float > 0
                ORDER BY (metrics->>'{metric}')::float DESC 
                LIMIT $2
            """, user_id, limit)
            
            return [self._row_to_content(row) for row in rows]
    
    async def search_content(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 50
    ) -> List[Content]:
        """Search content by text"""
        search_pattern = f"%{query}%"
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM content 
                WHERE user_id = $1 
                AND (text ILIKE $2 OR original_prompt ILIKE $2)
                ORDER BY 
                    CASE 
                        WHEN text ILIKE $2 THEN 1
                        WHEN original_prompt ILIKE $2 THEN 2
                        ELSE 3
                    END,
                    created_at DESC
                LIMIT $3
            """, user_id, search_pattern, limit)
            
            return [self._row_to_content(row) for row in rows]
    
    def _row_to_content(self, row) -> Content:
        """Convert database row to Content entity"""
        metrics_data = json.loads(row['metrics'] or '{}')
        metrics = ContentMetrics(
            impressions=metrics_data.get('impressions', 0),
            engagements=metrics_data.get('engagements', 0),
            likes=metrics_data.get('likes', 0),
            shares=metrics_data.get('shares', 0),
            comments=metrics_data.get('comments', 0),
            clicks=metrics_data.get('clicks', 0),
            saves=metrics_data.get('saves', 0),
            reach=metrics_data.get('reach', 0),
            engagement_rate=metrics_data.get('engagement_rate', 0.0),
            ctr=metrics_data.get('ctr', 0.0)
        )
        
        return Content(
            id=row['id'],
            user_id=row['user_id'],
            platform=Platform(row['platform']),
            content_type=ContentType(row['content_type']),
            status=ContentStatus(row['status']),
            text=row['text'],
            media_urls=json.loads(row['media_urls'] or '[]'),
            hashtags=json.loads(row['hashtags'] or '[]'),
            mentions=json.loads(row['mentions'] or '[]'),
            original_prompt=row['original_prompt'],
            ai_model_used=row['ai_model_used'],
            generation_parameters=json.loads(row['generation_parameters'] or '{}'),
            variants=json.loads(row['variants'] or '[]'),
            scheduled_for=row['scheduled_for'],
            published_at=row['published_at'],
            external_id=row['external_id'],
            external_url=row['external_url'],
            metrics=metrics,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _metrics_to_json(self, metrics: ContentMetrics) -> str:
        """Convert metrics to JSON string"""
        return json.dumps({
            'impressions': metrics.impressions,
            'engagements': metrics.engagements,
            'likes': metrics.likes,
            'shares': metrics.shares,
            'comments': metrics.comments,
            'clicks': metrics.clicks,
            'saves': metrics.saves,
            'reach': metrics.reach,
            'engagement_rate': metrics.engagement_rate,
            'ctr': metrics.ctr
        })