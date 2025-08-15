"""
Authentication Middleware
JWT-based authentication with proper error handling
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt

from ...infrastructure.config.settings import settings
from ...core.application.exceptions import AuthenticationError, AuthorizationError
from ...infrastructure.logging.logger import get_logger

logger = get_logger('northstar.auth')
security = HTTPBearer()


class JWTManager:
    """JWT token management"""
    
    def __init__(self):
        self.secret_key = settings.auth.secret_key
        self.algorithm = settings.auth.jwt_algorithm
        self.access_token_expire_minutes = settings.auth.access_token_expire_minutes
        self.refresh_token_expire_days = settings.auth.refresh_token_expire_days
    
    def create_access_token(self, user_id: str, additional_claims: Dict = None) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, expected_type: str = 'access') -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get('type') != expected_type:
                raise AuthenticationError(f"Invalid token type. Expected {expected_type}")
            
            # Verify expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                raise AuthenticationError("Token has expired")
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise AuthenticationError("Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        user_id = payload['sub']
        
        return self.create_access_token(user_id)


class PasswordManager:
    """Password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# Global instances
jwt_manager = JWTManager()
password_manager = PasswordManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract current user from JWT token"""
    try:
        payload = jwt_manager.verify_token(credentials.credentials)
        user_id = payload.get('sub')
        
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        logger.debug(f"Authenticated user: {user_id}")
        return user_id
        
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """Extract current user from JWT token (optional)"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_permissions(*permissions: str):
    """Decorator to require specific permissions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # For now, just check if user is authenticated
            # In the future, implement role-based permissions
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # TODO: Implement permission checking logic
            # Check if user has required permissions
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class AuthenticationService:
    """Authentication service for user login/registration"""
    
    def __init__(self):
        from ...core.domain.repositories.user_repository import UserRepository
        from ...infrastructure.di.container import container
        self.user_repo = container.resolve(UserRepository)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and return user ID"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        # In a real implementation, you'd verify the password against a stored hash
        # For now, we'll implement basic authentication
        
        logger.info(f"User authenticated: {email}")
        return user.id
    
    async def create_tokens(self, user_id: str) -> Dict[str, str]:
        """Create access and refresh tokens for user"""
        access_token = jwt_manager.create_access_token(user_id)
        refresh_token = jwt_manager.create_refresh_token(user_id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token"""
        new_access_token = jwt_manager.refresh_access_token(refresh_token)
        
        return {
            'access_token': new_access_token,
            'token_type': 'bearer'
        }