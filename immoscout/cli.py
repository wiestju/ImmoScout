"""Command-line interface: ``immoscout search`` and ``immoscout expose``."""
from __future__ import annotations

import argparse
import json
import sys

from .client import ImmoscoutClient
from .exceptions import ImmoscoutError
from .filters import SearchFilter


def _search(args: argparse.Namespace) -> int:
    client = ImmoscoutClient()
    query = SearchFilter(
        region=args.region,
        real_estate_type=args.type,
        price_min=args.price_min,
        price_max=args.price_max,
        rooms_min=args.rooms_min,
        living_space_min=args.space_min,
    )
    result = client.search(query)
    if args.json:
        rows = [listing.model_dump(exclude={"raw"}) for listing in result.listings[: args.limit]]
        print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
        return 0
    print(f"{result.total_results} results ({result.number_of_pages} pages)\n")
    for listing in result.listings[: args.limit]:
        price = f"{listing.price:.0f} {listing.currency or ''}".strip() if listing.price else "?"
        rooms = f"{listing.rooms:g} rooms" if listing.rooms else "?"
        space = f"{listing.living_space:g} m²" if listing.living_space else "?"
        print(f"• {listing.title or '(no title)'}")
        print(f"  {price} · {rooms} · {space} · {listing.address.line or ''}")
        print(f"  {listing.url}\n")
    return 0


def _expose(args: argparse.Namespace) -> int:
    expose = ImmoscoutClient().get_expose(args.expose_id)
    print(json.dumps(expose.model_dump(exclude={"raw"}), ensure_ascii=False, indent=2, default=str))
    return 0


def _regions(args: argparse.Namespace) -> int:
    for geo in ImmoscoutClient().suggest_regions(args.query):
        print(f"{geo.region:<40} {geo.type or '':<10} {geo.label or ''}")
    return 0


def _count(args: argparse.Namespace) -> int:
    total = ImmoscoutClient().count(
        SearchFilter(
            region=args.region,
            real_estate_type=args.type,
            price_min=args.price_min,
            price_max=args.price_max,
            rooms_min=args.rooms_min,
            living_space_min=args.space_min,
        )
    )
    print(total)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="immoscout", description="Search ImmobilienScout24.")
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="Search for listings")
    s.add_argument("--region", default="/de/berlin/berlin", help="Geocode path, e.g. /de/berlin/berlin")
    s.add_argument("--type", default="apartmentrent", help="apartmentrent, apartmentbuy, houserent, ...")
    s.add_argument("--price-min", type=float)
    s.add_argument("--price-max", type=float)
    s.add_argument("--rooms-min", type=float)
    s.add_argument("--space-min", type=float, help="Minimum living space in m²")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true", help="Output JSON")
    s.set_defaults(func=_search)

    e = sub.add_parser("expose", help="Fetch one listing's details")
    e.add_argument("expose_id")
    e.set_defaults(func=_expose)

    r = sub.add_parser("regions", help="Look up region geocode paths by name")
    r.add_argument("query", help="Place name, e.g. münchen")
    r.set_defaults(func=_regions)

    c = sub.add_parser("count", help="Count matching listings (no result pages)")
    c.add_argument("--region", default="/de/berlin/berlin", help="Geocode path or place name")
    c.add_argument("--type", default="apartmentrent")
    c.add_argument("--price-min", type=float)
    c.add_argument("--price-max", type=float)
    c.add_argument("--rooms-min", type=float)
    c.add_argument("--space-min", type=float)
    c.set_defaults(func=_count)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ImmoscoutError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
