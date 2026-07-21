"""Synchronous client for the (unofficial) ImmobilienScout24 mobile API."""
from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import requests

from .exceptions import NotFoundError, RateLimitError, RequestError
from .filters import SearchFilter
from .models import Expose, GeoLocation, Listing, SearchResult


class ImmoscoutClient:
    """Search ImmobilienScout24 listings and fetch expose details.

    Returns typed :class:`~immoscout.models.SearchResult` / :class:`Listing` /
    :class:`Expose` objects; the untouched API payload is always on ``.raw``.

    Args:
        user_agent: The mobile-app user agent to present.
        timeout: Per-request timeout in seconds (never hangs forever).
        max_retries: Retries on transient errors (429 / 5xx) with backoff.
        backoff: Base seconds for exponential backoff between retries.
    """

    BASE_URL = "https://api.mobile.immobilienscout24.de"
    DEFAULT_USER_AGENT = "ImmoScout_27.3_26.0_._iOS"

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff: float = 0.5,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.session = requests.Session()
        self.session.headers.update({"user-agent": user_agent})

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
            except requests.exceptions.RequestException as exc:
                last_exc = RequestError(f"Request to {url} failed: {exc}")
            else:
                status = response.status_code
                if status == 404:
                    raise NotFoundError(f"Resource not found: {url}")
                if status in (429, 403):
                    last_exc = RateLimitError(
                        f"Rate limited or blocked by ImmoScout (HTTP {status})."
                    )
                elif status >= 500:
                    last_exc = RequestError(f"Server error (HTTP {status}) for {url}.")
                elif not response.ok:
                    raise RequestError(f"HTTP {status} for {url}: {response.text[:200]}")
                else:
                    try:
                        return response.json()
                    except ValueError as exc:
                        raise RequestError(f"Invalid JSON from {url}: {exc}") from exc

            # transient error (429 / 5xx / network) → back off and retry
            if attempt < self.max_retries:
                time.sleep(self.backoff * (2**attempt))

        assert last_exc is not None
        raise last_exc

    def _prepare(self, filter: SearchFilter | None, kwargs: dict) -> SearchFilter:
        """Build the filter and resolve a plain-name region to a geocode path.

        ``region="München"`` is transparently resolved to ``"/de/bayern/muenchen"``
        via autocomplete; a region already starting with ``/`` is used as-is.
        """
        query = filter or SearchFilter(**kwargs)
        region = query.region or ""
        if region and not region.startswith("/"):
            matches = self.suggest_regions(region, limit=1)
            resolved = matches[0].region if matches else None
            if not resolved:
                raise RequestError(
                    f"Could not resolve region {region!r}; "
                    f"try client.suggest_regions({region!r}) to see options."
                )
            query = query.model_copy(update={"region": resolved})
        return query

    def search(self, filter: SearchFilter | None = None, **kwargs: Any) -> SearchResult:
        """Search for listings.

        Pass a :class:`SearchFilter`, or keyword arguments to build one inline.
        ``region`` may be a geocode path or a plain place name (auto-resolved)::

            client.search(region="München", price_max=1200, rooms_min=2)
        """
        query = self._prepare(filter, kwargs)
        data = self._request(
            "POST",
            "search/list",
            params=query.to_params(),
            json={"supportedResultListType": [], "userData": {}},
        )
        return SearchResult.from_api(data)

    def count(self, filter: SearchFilter | None = None, **kwargs: Any) -> int:
        """Return only the *number* of matching listings — no result pages fetched.

        Cheap way to answer "how many X are there?" ::

            client.count(region="Berlin", price_max=1000, rooms_min=2)
        """
        query = self._prepare(filter, kwargs)
        data = self._request("GET", "search/total", params=query.to_params())
        return int((data or {}).get("totalResults", 0))

    def search_all(
        self,
        filter: SearchFilter | None = None,
        *,
        max_pages: int | None = None,
        **kwargs: Any,
    ) -> Iterator[Listing]:
        """Iterate over every listing across all result pages (auto-paginating).

        Stops after ``max_pages`` pages if given. Be gentle — one request per page.
        """
        query = self._prepare(filter, kwargs)
        start_page = query.page
        page = start_page
        while True:
            result = self.search(query.model_copy(update={"page": page}))
            yield from result.listings
            if not result.listings or page >= result.number_of_pages:
                break
            if max_pages is not None and page - start_page + 1 >= max_pages:
                break
            page += 1

    def get_expose(self, expose_id: str | int) -> Expose:
        """Fetch full details for a single listing by its expose ID."""
        data = self._request("GET", f"expose/{expose_id}")
        return Expose.from_api(data)

    def suggest_regions(self, query: str, *, limit: int = 10) -> list[GeoLocation]:
        """Look up region geocode paths by name (autocomplete).

        Turns a place name into the ``region`` values ``search`` expects::

            client.suggest_regions("münchen")[0].region  # -> "/de/bayern/muenchen"
        """
        data = self._request("GET", "geoautocomplete/v3/locations.json", params={"i": query})
        items = data if isinstance(data, list) else []
        return [GeoLocation.from_api(item) for item in items[:limit]]
