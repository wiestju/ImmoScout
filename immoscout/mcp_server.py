"""Model Context Protocol (MCP) server for ImmobilienScout24.

Exposes ImmoScout search as tools any MCP client (Claude Desktop, Claude Code,
Cursor, …) can call natively, so an AI agent can look up real estate for you.

Run it:

    pip install "immoscout[mcp]"
    immoscout-mcp

Or wire it into Claude Desktop's ``mcpServers`` config with command ``immoscout-mcp``.
"""
from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:  # pragma: no cover
    FastMCP = None  # type: ignore[assignment]

from .client import ImmoscoutClient
from .filters import SearchFilter

_INSTALL_HINT = (
    "The MCP server needs the 'mcp' extra. Install it with:\n"
    '    pip install "immoscout[mcp]"'
)


def _build_server() -> FastMCP:
    mcp = FastMCP("immoscout")
    client = ImmoscoutClient()

    @mcp.tool()
    def search_listings(
        region: str = "/de/berlin/berlin",
        real_estate_type: str = "apartmentrent",
        price_min: float | None = None,
        price_max: float | None = None,
        rooms_min: float | None = None,
        rooms_max: float | None = None,
        living_space_min: float | None = None,
        max_results: int = 20,
    ) -> dict:
        """Search ImmobilienScout24 real-estate listings.

        Args:
            region: ImmoScout geocode path, e.g. "/de/berlin/berlin" or "/de/bayern/muenchen".
            real_estate_type: apartmentrent, apartmentbuy, houserent, housebuy, flatshareroom.
            price_min / price_max: monthly rent (or purchase price) bounds in EUR.
            rooms_min / rooms_max: number of rooms.
            living_space_min: minimum living space in m².
            max_results: how many listings to return (paginates as needed).
        """
        query = SearchFilter(
            region=region,
            real_estate_type=real_estate_type,
            price_min=price_min,
            price_max=price_max,
            rooms_min=rooms_min,
            rooms_max=rooms_max,
            living_space_min=living_space_min,
        )
        first = client.search(query)
        listings = []
        for listing in client.search_all(query):
            listings.append(listing.model_dump(exclude={"raw"}))
            if len(listings) >= max_results:
                break
        return {"total_results": first.total_results, "returned": len(listings), "listings": listings}

    @mcp.tool()
    def get_expose(expose_id: str) -> dict:
        """Fetch full details for a single listing by its ImmoScout expose ID."""
        return client.get_expose(expose_id).model_dump(exclude={"raw"})

    @mcp.tool()
    def count_listings(
        region: str = "/de/berlin/berlin",
        real_estate_type: str = "apartmentrent",
        price_min: float | None = None,
        price_max: float | None = None,
        rooms_min: float | None = None,
        living_space_min: float | None = None,
    ) -> dict:
        """Count matching listings without fetching them. ``region`` may be a place name."""
        total = client.count(
            SearchFilter(
                region=region,
                real_estate_type=real_estate_type,
                price_min=price_min,
                price_max=price_max,
                rooms_min=rooms_min,
                living_space_min=living_space_min,
            )
        )
        return {"total_results": total}

    @mcp.tool()
    def suggest_regions(query: str) -> list[dict]:
        """Resolve a place name to ImmoScout region paths for use with search_listings.

        Example: suggest_regions("münchen") -> [{"label": "München", "region": "/de/bayern/muenchen", ...}]
        """
        return [geo.model_dump(exclude={"raw"}) for geo in client.suggest_regions(query)]

    return mcp


def main() -> None:
    if FastMCP is None:
        raise SystemExit(_INSTALL_HINT)
    _build_server().run()


if __name__ == "__main__":
    main()
