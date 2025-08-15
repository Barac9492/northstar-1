"""
Rate Limiting Middleware
Redis-based rate limiting with tier-specific limits
"""
from fastapi import HTTPException, Request, Depends
from typing import Dict, Optional, Callable
import time
import hashlib
from functools import wraps
import redis.asyncio as redis

from ...infrastructure.config.settings import settings
from ...core.application.exceptions import RateLimitExceededError
from ...infrastructure.logging.logger import get_logger

logger = get_logger('northstar.rate_limiting')


class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(settings.redis.url)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int,
        identifier: str = None
    ) -> tuple[bool, Dict]:
        """Check if request is allowed based on rate limit"""
        
        if not self.redis_client:
            # If Redis is not available, allow all requests
            logger.warning("Redis not available, allowing all requests")
            return True, {}
        
        try:
            # Create rate limit key
            rate_key = f"rate_limit:{key}"
            if identifier:
                rate_key += f":{identifier}"
            
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Use sliding window approach
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            await pipe.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests
            current_count = await pipe.zcard(rate_key)
            
            if current_count < limit:
                # Add current request
                await pipe.zadd(rate_key, {str(current_time): current_time})
                await pipe.expire(rate_key, window_seconds)
                await pipe.execute()
                
                remaining = limit - current_count - 1
                reset_time = current_time + window_seconds
                
                return True, {
                    'limit': limit,
                    'remaining': remaining,
                    'reset': reset_time,
                    'retry_after': None
                }
            else:
                # Rate limit exceeded
                reset_time = current_time + window_seconds
                retry_after = window_seconds
                
                return False, {
                    'limit': limit,
                    'remaining': 0,
                    'reset': reset_time,
                    'retry_after': retry_after
                }
                
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # If there's an error, allow the request
            return True, {}
    
    async def get_user_tier_limits(self, user_id: str) -> Dict[str, int]:
        """Get rate limits based on user tier"""
        # This would typically query the database for user tier
        # For now, return default limits
        return {
            'per_minute': settings.rate_limit.default_per_minute,
            'per_hour': settings.rate_limit.default_per_hour,
            'per_day': settings.rate_limit.default_per_day
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(
    operation: str,
    per_minute: Optional[int] = None,
    per_hour: Optional[int] = None,
    per_day: Optional[int] = None,
    key_func: Optional[Callable] = None
):
    """Rate limiting decorator"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and user info
            request = None
            user_id = None
            
            # Look for request in args (FastAPI injects it)
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Look for user_id in kwargs
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            
            if not request:
                # If no request object, skip rate limiting
                return await func(*args, **kwargs)
            
            # Create rate limit key
            if key_func:
                identifier = key_func(request, user_id)
            else:
                identifier = user_id or request.client.host
            
            # Check different time windows
            checks = []
            if per_minute:
                checks.append((f"{operation}_per_minute", per_minute, 60))
            if per_hour:
                checks.append((f"{operation}_per_hour", per_hour, 3600))
            if per_day:
                checks.append((f"{operation}_per_day", per_day, 86400))
            
            # Perform rate limit checks
            for key_suffix, limit, window in checks:
                allowed, info = await rate_limiter.is_allowed(
                    f"{key_suffix}:{identifier}",
                    limit,
                    window,
                    identifier
                )
                
                if not allowed:
                    logger.warning(
                        f"Rate limit exceeded for {operation}",
                        extra={
                            'user_id': user_id,
                            'identifier': identifier,
                            'operation': operation,
                            'limit': limit,
                            'window': window
                        }
                    )
                    
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded for {operation}",
                        headers={
                            'X-RateLimit-Limit': str(info['limit']),
                            'X-RateLimit-Remaining': str(info['remaining']),
                            'X-RateLimit-Reset': str(info['reset']),
                            'Retry-After': str(info['retry_after'])
                        }
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimitMiddleware:
    """Middleware for global rate limiting"""
    
    def __init__(self):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """Apply global rate limiting"""
        
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/metrics']:
            return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host if request.client else 'unknown'
        
        # Apply global rate limit
        allowed, info = await self.rate_limiter.is_allowed(
            f"global:{client_ip}",
            settings.rate_limit.default_per_minute,
            60,
            client_ip
        )
        
        if not allowed:
            logger.warning(
                f"Global rate limit exceeded",
                extra={
                    'client_ip': client_ip,
                    'path': request.url.path,
                    'method': request.method
                }
            )
            
            return HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': str(info['remaining']),
                    'X-RateLimit-Reset': str(info['reset']),
                    'Retry-After': str(info['retry_after'])
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(info['reset'])
        
        return response


def create_user_rate_limit_key(request: Request, user_id: Optional[str]) -> str:
    """Create rate limit key based on user or IP"""
    if user_id:
        return f"user:{user_id}"
    return f"ip:{request.client.host if request.client else 'unknown'}"


# Predefined rate limit decorators
content_generation_rate_limit = rate_limit(
    'content_generation',
    per_hour=settings.rate_limit.content_generation_per_hour,
    key_func=create_user_rate_limit_key
)

engagement_rate_limit = rate_limit(
    'engagement',
    per_day=settings.rate_limit.engagement_per_day,
    key_func=create_user_rate_limit_key
)