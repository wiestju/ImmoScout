"""Typed models that turn ImmoScout's raw JSON into clean Python objects.

Every model keeps the original payload on ``.raw`` so nothing is lost — the
typed fields are a convenience layer, not a cage.
"""
from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

_EXPOSE_URL = "https://www.immobilienscout24.de/expose/{id}"


def parse_german_number(text: str | None) -> float | None:
    """Parse a German-formatted number out of a string.

    Handles thousands separators and decimal commas: ``"1.380,50 €" -> 1380.5``,
    ``"27,83 m²" -> 27.83``, ``"1 Zi." -> 1.0``. Returns ``None`` if no number.
    """
    if not text:
        return None
    match = re.search(r"\d[\d.]*(?:,\d+)?", text)
    if not match:
        return None
    token = match.group(0).replace(".", "").replace(",", ".")
    try:
        return float(token)
    except ValueError:
        return None


class Address(BaseModel):
    """A listing's location."""

    line: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    def __str__(self) -> str:
        return self.line or ""


class Listing(BaseModel):
    """A single search result (one apartment/house)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str | None = None
    url: str | None = None
    address: Address = Field(default_factory=Address)
    price: float | None = None
    currency: str | None = None
    living_space: float | None = None  # m²
    rooms: float | None = None
    real_estate_type: str | None = None
    listing_type: str | None = None
    published: str | None = None
    is_private: bool = False
    is_new: bool = False
    is_project: bool = False
    picture_url: str | None = None
    raw: dict = Field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, item: dict) -> Listing:
        addr = item.get("address") or {}
        price = living_space = rooms = None
        currency = None
        for attr in item.get("attributes") or []:
            value = (attr.get("value") or "").strip()
            if "€" in value:
                price, currency = parse_german_number(value), "EUR"
            elif "m²" in value or "m2" in value:
                living_space = parse_german_number(value)
            elif "Zi" in value:
                rooms = parse_german_number(value)
        item_id = str(item.get("id", ""))
        return cls(
            id=item_id,
            title=item.get("title"),
            url=_EXPOSE_URL.format(id=item_id) if item_id else None,
            address=Address(
                line=addr.get("line"), latitude=addr.get("lat"), longitude=addr.get("lon")
            ),
            price=price,
            currency=currency,
            living_space=living_space,
            rooms=rooms,
            real_estate_type=item.get("realEstateType"),
            listing_type=item.get("listingType"),
            published=item.get("published"),
            is_private=bool(item.get("isPrivate", False)),
            is_new=bool(item.get("isNewObject", False)),
            is_project=bool(item.get("isProject", False)),
            picture_url=(item.get("titlePicture") or {}).get("full"),
            raw=item,
        )


class SearchResult(BaseModel):
    """One page of search results plus its pagination metadata."""

    total_results: int = 0
    page_number: int = 1
    page_size: int = 0
    number_of_pages: int = 0
    listings: list[Listing] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict, repr=False)

    def __iter__(self):  # type: ignore[override]
        return iter(self.listings)

    def __len__(self) -> int:
        return len(self.listings)

    @classmethod
    def from_api(cls, data: dict) -> SearchResult:
        items = data.get("resultListItems") or []
        listings = [
            Listing.from_api(it["item"])
            for it in items
            if it.get("type") == "EXPOSE_RESULT" and it.get("item")
        ]
        return cls(
            total_results=data.get("totalResults", 0),
            page_number=data.get("pageNumber", 1),
            page_size=data.get("pageSize", 0),
            number_of_pages=data.get("numberOfPages", 0),
            listings=listings,
            raw=data,
        )


class GeoLocation(BaseModel):
    """A place suggestion from region autocomplete.

    ``region`` is the geocode path you pass to :class:`SearchFilter` / ``search``,
    e.g. ``"/de/bayern/muenchen"``.
    """

    label: str | None = None
    region: str | None = None
    type: str | None = None
    id: str | None = None
    raw: dict = Field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, item: dict) -> GeoLocation:
        entity = item.get("entity") or item
        geo_id = entity.get("id")
        return cls(
            label=entity.get("label"),
            region=(entity.get("geopath") or {}).get("uri"),
            type=entity.get("type"),
            id=str(geo_id) if geo_id is not None else None,
            raw=item,
        )


class Expose(BaseModel):
    """Detailed view of a single listing (from ``get_expose``).

    ImmoScout's expose payload is a deeply nested, section-based structure that
    changes often; this model surfaces the useful bits and keeps everything on
    ``.raw`` for full access.
    """

    id: str
    title: str | None = None
    real_estate_type: str | None = None
    address: str | None = None
    price: float | None = None
    living_space: float | None = None
    rooms: float | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
    description: str | None = None
    url: str | None = None
    raw: dict = Field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict) -> Expose:
        header = data.get("header") or {}
        sections = data.get("sections") or []
        attributes: dict[str, str] = {}
        description_parts: list[str] = []
        address: str | None = None

        for section in sections:
            stype = section.get("type")
            if stype in ("TOP_ATTRIBUTES", "ATTRIBUTE_LIST", "PRICE_INFO"):
                for attr in section.get("attributes") or []:
                    label = (attr.get("label") or "").strip().rstrip(":")
                    text = (attr.get("text") or attr.get("value") or "").strip()
                    if label and text:
                        attributes.setdefault(label, text)
            elif stype == "TEXT_AREA":
                text = section.get("text")
                if text:
                    description_parts.append(text.strip())
            elif stype == "MAP" and address is None:
                address = " ".join(
                    p for p in (section.get("addressLine1"), section.get("addressLine2")) if p
                ) or None

        def pick(*needles: str) -> str | None:
            for label, value in attributes.items():
                low = label.lower()
                if any(n in low for n in needles):
                    return value
            return None

        eid = str(header.get("id") or data.get("id") or "")
        return cls(
            id=eid,
            title=header.get("title"),
            real_estate_type=header.get("realEstateType"),
            address=address,
            price=parse_german_number(pick("kaltmiete", "miete", "kaufpreis")),
            living_space=parse_german_number(pick("wohnfläche", "fläche")),
            rooms=parse_german_number(pick("zimmer")),
            attributes=attributes,
            description="\n\n".join(description_parts) or None,
            url=_EXPOSE_URL.format(id=eid) if eid else None,
            raw=data,
        )
