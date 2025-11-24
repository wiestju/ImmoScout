class ImmoscoutError(Exception):
    """Base exception for Immoscout API errors."""
    pass

class RequestError(ImmoscoutError):
    """Raised when an HTTP request fails."""
    pass

class NotFoundError(ImmoscoutError):
    """Raised when a resource is not found (404)."""
    pass
