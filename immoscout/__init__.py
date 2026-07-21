"""Typed, unofficial Python client for ImmobilienScout24."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .client import ImmoscoutClient
from .exceptions import (
    ImmoscoutError,
    NotFoundError,
    RateLimitError,
    RequestError,
)
from .filters import RealEstateType, SearchFilter
from .models import Address, Expose, GeoLocation, Listing, SearchResult

try:
    __version__ = version("immoscout")
except PackageNotFoundError:  # running from a source checkout without install
    __version__ = "0.0.0.dev0"

__all__ = [
    "ImmoscoutClient",
    "SearchFilter",
    "RealEstateType",
    "SearchResult",
    "Listing",
    "Expose",
    "Address",
    "GeoLocation",
    "ImmoscoutError",
    "RequestError",
    "NotFoundError",
    "RateLimitError",
    "__version__",
]
