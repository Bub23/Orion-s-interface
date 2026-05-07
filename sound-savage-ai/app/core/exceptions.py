"""
Custom exception classes
"""


class SoundSavageException(Exception):
    """Base exception"""
    pass


class InvalidCredentials(SoundSavageException):
    """Invalid login credentials"""
    pass


class UserAlreadyExists(SoundSavageException):
    """User already registered"""
    pass


class UserNotFound(SoundSavageException):
    """User not found"""
    pass


class InvalidToken(SoundSavageException):
    """Invalid or expired JWT"""
    pass


class ContentNotFound(SoundSavageException):
    """Content idea not found"""
    pass


class RenderFailed(SoundSavageException):
    """Video render failed"""
    pass


class SubscriptionError(SoundSavageException):
    """Subscription-related error"""
    pass
