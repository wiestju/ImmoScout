"""Exception hierarchy for the ImmoScout client."""


class ImmoscoutError(Exception):
    """Base exception for all ImmoScout errors."""


class RequestError(ImmoscoutError):
    """An HTTP request failed (network error or non-2xx response)."""


class NotFoundError(RequestError):
    """A resource was not found (HTTP 404)."""


class RateLimitError(RequestError):
    """The API is rate limiting or blocking the client (HTTP 429 / 403).

    ImmobilienScout24 actively throttles automated access — back off and slow
    down rather than retrying aggressively.
    """
