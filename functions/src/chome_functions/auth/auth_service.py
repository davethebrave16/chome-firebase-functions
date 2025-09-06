"""Authentication service for Firebase Functions."""

from firebase_functions import https_fn
from typing import Optional

from ..config.settings import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.secret = settings.secret
        if not self.secret:
            raise ValueError("SECRET environment variable is required")
    
    def verify_token(self, request: https_fn.Request) -> bool:
        """
        Verify the authorization token from the request.
        
        Args:
            request: The HTTP request object
            
        Returns:
            True if the token is valid, False otherwise
        """
        try:
            token = request.headers.get("Authorization")
            if not token:
                logger.warning("No authorization token provided")
                return False
            
            is_valid = token == self.secret
            if not is_valid:
                logger.warning("Invalid authorization token provided")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return False


# Global auth service instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create the auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def verify_token(request: https_fn.Request) -> bool:
    """
    Convenience function to verify token using the global auth service.
    
    Args:
        request: The HTTP request object
        
    Returns:
        True if the token is valid, False otherwise
    """
    try:
        auth_service = get_auth_service()
        return auth_service.verify_token(request)
    except Exception as e:
        logger.error(f"Error in verify_token: {str(e)}")
        return False
