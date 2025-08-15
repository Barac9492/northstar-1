"""
PostgreSQL Implementation of User Repository
Concrete implementation of the user repository interface
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import asyncpg
import json

from ....core.domain.entities.user import User, UserTier, UserStatus
from ....core.domain.repositories.user_repository import UserRepository
from ...di.container import service


@service(UserRepository, 'singleton')
class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL implementation of user repository"""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (
                    id, email, name, company, tier, status, 
                    monthly_generations, monthly_engagements, 
                    last_activity, preferences, connected_platforms,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """, 
                user.id, user.email, user.name, user.company,
                user.tier.value, user.status.value,
                user.monthly_generations, user.monthly_engagements,
                user.last_activity, json.dumps(user.preferences),
                json.dumps(user.connected_platforms),
                user.created_at, user.updated_at
            )
            
            return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1", user_id
            )
            
            if not row:
                return None
            
            return self._row_to_user(row)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1", email
            )
            
            if not row:
                return None
            
            return self._row_to_user(row)
    
    async def update(self, user: User) -> User:
        """Update existing user"""
        user.updated_at = datetime.utcnow()
        
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE users SET 
                    email = $2, name = $3, company = $4, tier = $5, status = $6,
                    monthly_generations = $7, monthly_engagements = $8, 
                    last_activity = $9, preferences = $10, connected_platforms = $11,
                    updated_at = $12
                WHERE id = $1
            """,
                user.id, user.email, user.name, user.company,
                user.tier.value, user.status.value,
                user.monthly_generations, user.monthly_engagements,
                user.last_activity, json.dumps(user.preferences),
                json.dumps(user.connected_platforms), user.updated_at
            )
            
            return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE id = $1", user_id
            )
            
            return result == "DELETE 1"
    
    async def list_by_tier(self, tier: UserTier, limit: int = 100, offset: int = 0) -> List[User]:
        """Get users by tier with pagination"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM users 
                WHERE tier = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
            """, tier.value, limit, offset)
            
            return [self._row_to_user(row) for row in rows]
    
    async def list_by_status(self, status: UserStatus, limit: int = 100, offset: int = 0) -> List[User]:
        """Get users by status with pagination"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM users 
                WHERE status = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
            """, status.value, limit, offset)
            
            return [self._row_to_user(row) for row in rows]
    
    async def count_by_tier(self, tier: UserTier) -> int:
        """Count users by tier"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE tier = $1", tier.value
            )
            
            return result
    
    async def get_usage_stats(self, user_id: str) -> Dict:
        """Get user usage statistics"""
        async with self.db_pool.acquire() as conn:
            user_stats = await conn.fetchrow("""
                SELECT 
                    monthly_generations,
                    monthly_engagements,
                    last_activity,
                    tier
                FROM users WHERE id = $1
            """, user_id)
            
            if not user_stats:
                return {}
            
            # Get content count
            content_count = await conn.fetchval("""
                SELECT COUNT(*) FROM content WHERE user_id = $1
            """, user_id)
            
            # Get published content count
            published_count = await conn.fetchval("""
                SELECT COUNT(*) FROM content 
                WHERE user_id = $1 AND status = 'published'
            """, user_id)
            
            return {
                'monthly_generations': user_stats['monthly_generations'],
                'monthly_engagements': user_stats['monthly_engagements'],
                'last_activity': user_stats['last_activity'],
                'tier': user_stats['tier'],
                'total_content': content_count,
                'published_content': published_count
            }
    
    async def reset_monthly_usage(self, user_ids: List[str]) -> int:
        """Reset monthly usage for multiple users"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE users SET 
                    monthly_generations = 0,
                    monthly_engagements = 0,
                    updated_at = $1
                WHERE id = ANY($2)
            """, datetime.utcnow(), user_ids)
            
            # Extract number from "UPDATE n" result
            return int(result.split()[-1])
    
    async def find_inactive_users(self, days: int) -> List[User]:
        """Find users inactive for specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM users 
                WHERE last_activity < $1 OR last_activity IS NULL
                ORDER BY last_activity ASC NULLS FIRST
            """, cutoff_date)
            
            return [self._row_to_user(row) for row in rows]
    
    async def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by email, name, or company"""
        search_pattern = f"%{query}%"
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM users 
                WHERE email ILIKE $1 
                   OR name ILIKE $1 
                   OR company ILIKE $1
                ORDER BY 
                    CASE 
                        WHEN email = $2 THEN 1
                        WHEN email ILIKE $1 THEN 2
                        WHEN name ILIKE $1 THEN 3
                        ELSE 4
                    END,
                    created_at DESC
                LIMIT $3
            """, search_pattern, query, limit)
            
            return [self._row_to_user(row) for row in rows]
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User entity"""
        return User(
            id=row['id'],
            email=row['email'],
            name=row['name'],
            company=row['company'],
            tier=UserTier(row['tier']),
            status=UserStatus(row['status']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            monthly_generations=row['monthly_generations'],
            monthly_engagements=row['monthly_engagements'],
            last_activity=row['last_activity'],
            preferences=json.loads(row['preferences'] or '{}'),
            connected_platforms=json.loads(row['connected_platforms'] or '[]')
        )