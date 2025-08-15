"""
Global Error Handler Middleware
Centralized error handling with proper logging and user-friendly responses
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
from typing import Dict, Any

from ...core.application.exceptions import (
    ApplicationError,
    UserNotFoundError,
    InsufficientCreditsError,
    ContentGenerationError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
    ExternalServiceError,
    ConfigurationError
)
from ...infrastructure.logging.logger import get_logger

logger = get_logger('northstar.error_handler')


class GlobalErrorHandler(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle different types of exceptions"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log the exception
        logger.error(
            f"Unhandled exception in {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'exception_type': type(exc).__name__,
                'exception_message': str(exc),
                'path': request.url.path,
                'method': request.method
            },
            exc_info=True
        )
        
        # Handle specific application exceptions
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    'error': {
                        'code': exc.status_code,
                        'message': exc.detail,
                        'request_id': request_id
                    }
                }
            )
        
        # Handle custom application exceptions
        error_mappings = {
            UserNotFoundError: (404, "User not found"),
            InsufficientCreditsError: (402, "Insufficient credits"),
            ContentGenerationError: (500, "Content generation failed"),
            ValidationError: (400, "Validation error"),
            AuthenticationError: (401, "Authentication failed"),
            AuthorizationError: (403, "Access denied"),
            RateLimitExceededError: (429, "Rate limit exceeded"),
            ExternalServiceError: (502, "External service unavailable"),
            ConfigurationError: (500, "Configuration error")
        }
        
        for exc_type, (status_code, default_message) in error_mappings.items():
            if isinstance(exc, exc_type):
                return JSONResponse(
                    status_code=status_code,
                    content={
                        'error': {
                            'code': exc.error_code if hasattr(exc, 'error_code') else exc_type.__name__,
                            'message': str(exc) or default_message,
                            'request_id': request_id
                        }
                    }
                )
        
        # Handle other application errors
        if isinstance(exc, ApplicationError):
            return JSONResponse(
                status_code=500,
                content={
                    'error': {
                        'code': exc.error_code or 'APPLICATION_ERROR',
                        'message': str(exc) or 'An application error occurred',
                        'request_id': request_id
                    }
                }
            )
        
        # Handle unexpected exceptions
        return JSONResponse(
            status_code=500,
            content={
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'An unexpected error occurred',
                    'request_id': request_id
                }
            }
        )


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> JSONResponse:
    """Create standardized error response"""
    
    error_content = {
        'error': {
            'code': error_code,
            'message': message,
            'request_id': request_id
        }
    }
    
    if details:
        error_content['error']['details'] = details
    
    return JSONResponse(
        status_code=status_code,
        content=error_content
    )


def handle_validation_error(exc) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            'field': '.'.join(str(x) for x in error['loc']),
            'message': error['msg'],
            'type': error['type']
        })
    
    return create_error_response(
        status_code=422,
        error_code='VALIDATION_ERROR',
        message='Input validation failed',
        details={'validation_errors': errors}
    )


class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.logger = get_logger('northstar.error_context')
    
    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(
                f"Operation failed: {self.operation} - {str(exc_val)}",
                extra={
                    **self.context,
                    'exception_type': exc_type.__name__,
                    'exception_message': str(exc_val)
                },
                exc_info=True
            )
            return False  # Don't suppress the exception
        else:
            self.logger.debug(f"Operation completed: {self.operation}", extra=self.context)
            return True