"""
Enterprise Logging Infrastructure
Structured logging with multiple output formats and levels
"""
import logging
import logging.config
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..config.settings import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class ContextualLogger:
    """Logger with contextual information"""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set context for subsequent log messages"""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear context"""
        self._context.clear()
    
    def _log_with_context(self, level: int, message: str, *args, **kwargs) -> None:
        """Log message with context"""
        extra = kwargs.get('extra', {})
        extra.update(self._context)
        kwargs['extra'] = extra
        self._logger.log(level, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        self._log_with_context(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        self._log_with_context(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        self._log_with_context(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        self._log_with_context(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        self._log_with_context(logging.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        kwargs['exc_info'] = True
        self.error(message, *args, **kwargs)


def setup_logging() -> None:
    """Setup application logging configuration"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Determine log level
    log_level = getattr(logging, settings.monitoring.log_level.upper(), logging.INFO)
    
    # Configure logging
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'json' if settings.monitoring.log_format == 'json' else 'detailed',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'json' if settings.monitoring.log_format == 'json' else 'detailed',
                'filename': logs_dir / 'app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.ERROR,
                'formatter': 'json' if settings.monitoring.log_format == 'json' else 'detailed',
                'filename': logs_dir / 'error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'level': log_level,
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'northstar': {  # Application logger
                'level': log_level,
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'uvicorn': {
                'level': logging.INFO,
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'asyncpg': {
                'level': logging.WARNING,
                'handlers': ['console', 'file'],
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(config)


def get_logger(name: str = 'northstar') -> ContextualLogger:
    """Get a contextual logger instance"""
    setup_logging()
    return ContextualLogger(logging.getLogger(name))


# Global logger instance
logger = get_logger()


class LoggerMiddleware:
    """Middleware for request/response logging"""
    
    def __init__(self):
        self.logger = get_logger('northstar.middleware')
    
    async def __call__(self, request, call_next):
        """Log requests and responses"""
        start_time = datetime.utcnow()
        
        # Log request
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'request_id': getattr(request.state, 'request_id', None),
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'user_agent': request.headers.get('user-agent'),
                'ip': request.client.host if request.client else None
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    'request_id': getattr(request.state, 'request_id', None),
                    'status_code': response.status_code,
                    'duration_seconds': duration
                }
            )
            
            return response
            
        except Exception as e:
            # Log error
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    'request_id': getattr(request.state, 'request_id', None),
                    'error': str(e),
                    'duration_seconds': duration
                },
                exc_info=True
            )
            raise


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        func_logger = get_logger(f'northstar.{func.__module__}')
        func_logger.debug(
            f"Calling {func.__name__}",
            extra={
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
        )
        
        try:
            result = func(*args, **kwargs)
            func_logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            func_logger.error(
                f"Function {func.__name__} failed: {str(e)}",
                extra={'error': str(e)},
                exc_info=True
            )
            raise
    
    return wrapper