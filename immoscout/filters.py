"""Typed, validated search filters that compile to ImmoScout API parameters."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RealEstateType(str, Enum):
    """The kind of property to search for."""

    APARTMENT_RENT = "apartmentrent"
    APARTMENT_BUY = "apartmentbuy"
    HOUSE_RENT = "houserent"
    HOUSE_BUY = "housebuy"
    FLAT_SHARE_ROOM = "flatshareroom"
    GARAGE_RENT = "garagerent"
    GARAGE_BUY = "garagebuy"


def _fmt(value: float | None) -> str:
    return "" if value is None else str(float(value))


def _range(low: float | None, high: float | None) -> str | None:
    """ImmoScout range params look like ``"500.0-800.0"``, ``"50.0-"`` or ``"-1000.0"``."""
    if low is None and high is None:
        return None
    return f"{_fmt(low)}-{_fmt(high)}"


class SearchFilter(BaseModel):
    """A validated search query. Compile it to API params with ``to_params()``.

    Example::

        SearchFilter(region="/de/berlin/berlin", price_max=1200, rooms_min=2)
    """

    region: str = "/de/berlin/berlin"
    real_estate_type: RealEstateType | str = RealEstateType.APARTMENT_RENT
    price_type: str = "calculatedtotalrent"
    price_min: float | None = None
    price_max: float | None = None
    rooms_min: float | None = None
    rooms_max: float | None = None
    living_space_min: float | None = None
    living_space_max: float | None = None
    page: int = Field(default=1, ge=1)
    # Any additional raw API parameters, passed through as-is.
    extra: dict[str, str] = Field(default_factory=dict)

    def to_params(self) -> dict:
        ret = str(getattr(self.real_estate_type, "value", self.real_estate_type))
        params: dict = {
            "searchType": "region",
            "geocodes": self.region,
            "realestatetype": ret,
            "pricetype": self.price_type,
            "pagenumber": self.page,
        }
        if (price := _range(self.price_min, self.price_max)) is not None:
            params["price"] = price
        if (rooms := _range(self.rooms_min, self.rooms_max)) is not None:
            params["numberofrooms"] = rooms
        if (space := _range(self.living_space_min, self.living_space_max)) is not None:
            params["livingspace"] = space
        params.update(self.extra)
        return params
