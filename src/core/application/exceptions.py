"""
Application Layer Exceptions
Custom exceptions for business logic errors
"""


class ApplicationError(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UserNotFoundError(ApplicationError):
    """Raised when user is not found"""
    
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")


class InsufficientCreditsError(ApplicationError):
    """Raised when user has insufficient credits/limits"""
    
    def __init__(self, message: str = "Insufficient credits"):
        super().__init__(message, "INSUFFICIENT_CREDITS")


class ContentGenerationError(ApplicationError):
    """Raised when content generation fails"""
    
    def __init__(self, message: str = "Content generation failed"):
        super().__init__(message, "CONTENT_GENERATION_ERROR")


class ValidationError(ApplicationError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(ApplicationError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(ApplicationError):
    """Raised when user is not authorized"""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class RateLimitExceededError(ApplicationError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")


class ExternalServiceError(ApplicationError):
    """Raised when external service fails"""
    
    def __init__(self, message: str = "External service error", service: str = None):
        self.service = service
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, "CONFIGURATION_ERROR")