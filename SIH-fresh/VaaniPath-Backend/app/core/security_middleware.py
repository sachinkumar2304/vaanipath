"""
VaaniPath Security Middleware
Implements enterprise-grade security features including:
- Rate limiting
- Security headers
- Request logging
- Input sanitization
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import bleach
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Account lockout tracking
failed_login_attempts = defaultdict(list)
LOCKOUT_THRESHOLD = 5  # Lock after 5 failed attempts
LOCKOUT_DURATION = 30 * 60  # 30 minutes in seconds


async def security_headers_middleware(request: Request, call_next: Callable):
    """
    Add security headers to all responses
    
    Headers added:
    - X-Frame-Options: Prevents clickjacking
    - X-Content-Type-Options: Prevents MIME sniffing
    - X-XSS-Protection: Enables XSS filter
    - Content-Security-Policy: Restricts resource loading
    - Strict-Transport-Security: Enforces HTTPS
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Controls browser features
    """
    response = await call_next(request)
    
    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Content Security Policy - restrict resource loading
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:; "
        "media-src 'self' https:; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    # Enforce HTTPS (only in production)
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    
    # Control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Control browser features
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    
    return response


async def request_logging_middleware(request: Request, call_next: Callable):
    """
    Log all incoming requests for security monitoring
    
    Logs:
    - Request method and path
    - Client IP address
    - Response status code
    - Request duration
    - Failed authentication attempts
    """
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response: {response.status_code} "
        f"for {request.method} {request.url.path} "
        f"({duration:.2f}s)"
    )
    
    # Log failed authentication attempts
    if request.url.path in ["/api/auth/login", "/api/auth/signup"]:
        if response.status_code == 401:
            logger.warning(
                f"Failed authentication attempt from "
                f"{request.client.host if request.client else 'unknown'} "
                f"on {request.url.path}"
            )
    
    return response


def check_account_lockout(email: str) -> bool:
    """
    Check if account is locked due to too many failed login attempts
    
    Args:
        email: User email address
        
    Returns:
        True if account is locked, False otherwise
    """
    if email not in failed_login_attempts:
        return False
    
    # Clean old attempts (older than lockout duration)
    cutoff_time = datetime.now() - timedelta(seconds=LOCKOUT_DURATION)
    failed_login_attempts[email] = [
        attempt for attempt in failed_login_attempts[email]
        if attempt > cutoff_time
    ]
    
    # Check if locked
    if len(failed_login_attempts[email]) >= LOCKOUT_THRESHOLD:
        logger.warning(f"Account locked: {email}")
        return True
    
    return False


def record_failed_login(email: str):
    """
    Record a failed login attempt
    
    Args:
        email: User email address
    """
    failed_login_attempts[email].append(datetime.now())
    logger.info(
        f"Failed login attempt #{len(failed_login_attempts[email])} "
        f"for {email}"
    )


def reset_failed_logins(email: str):
    """
    Reset failed login attempts after successful login
    
    Args:
        email: User email address
    """
    if email in failed_login_attempts:
        del failed_login_attempts[email]
        logger.info(f"Reset failed login attempts for {email}")


def sanitize_input(text: str, allowed_tags: list = None) -> str:
    """
    Sanitize user input to prevent XSS attacks
    
    Args:
        text: Input text to sanitize
        allowed_tags: List of allowed HTML tags (default: none)
        
    Returns:
        Sanitized text with HTML tags removed/escaped
    """
    if allowed_tags is None:
        allowed_tags = []
    
    # Remove/escape HTML tags
    cleaned = bleach.clean(
        text,
        tags=allowed_tags,
        strip=True,
        strip_comments=True
    )
    
    return cleaned


def validate_file_upload(filename: str, content_type: str, max_size_mb: int = 100) -> bool:
    """
    Validate file uploads for security
    
    Args:
        filename: Name of the uploaded file
        content_type: MIME type of the file
        max_size_mb: Maximum allowed file size in MB
        
    Returns:
        True if file is valid, raises HTTPException otherwise
    """
    # Allowed file extensions
    allowed_extensions = {
        'video': ['.mp4', '.webm', '.mov', '.avi'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt']
    }
    
    # Allowed MIME types
    allowed_mimes = {
        'video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo',
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    # Check file extension
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    valid_ext = any(
        file_ext in exts 
        for exts in allowed_extensions.values()
    )
    
    if not valid_ext:
        logger.warning(f"Invalid file extension: {file_ext} for {filename}")
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(sum(allowed_extensions.values(), []))}"
        )
    
    # Check MIME type
    if content_type not in allowed_mimes:
        logger.warning(f"Invalid MIME type: {content_type} for {filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {content_type}"
        )
    
    logger.info(f"File upload validated: {filename} ({content_type})")
    return True


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors
    
    Returns a JSON response with retry information
    """
    logger.warning(
        f"Rate limit exceeded for {request.client.host if request.client else 'unknown'} "
        f"on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail
        }
    )


# Export all security functions
__all__ = [
    'limiter',
    'security_headers_middleware',
    'request_logging_middleware',
    'check_account_lockout',
    'record_failed_login',
    'reset_failed_logins',
    'sanitize_input',
    'validate_file_upload',
    'rate_limit_exceeded_handler'
]
