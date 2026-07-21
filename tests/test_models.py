from immoscout.models import Expose, Listing, SearchResult, parse_german_number

SEARCH_ITEM = {
    "id": "169446368",
    "title": "Helles Zimmer in einer 3er-WG",
    "reportUrl": "https://angebot-melden.immobilienscout24.de/report?realEstateId=169446368",
    "titlePicture": {"full": "https://pictures.immobilienscout24.de/x.jpg"},
    "address": {"line": "Roedernallee 118H, 13437 Berlin", "lat": 52.58927, "lon": 13.33868},
    "isPrivate": False,
    "isNewObject": True,
    "listingType": "XL",
    "published": "vor einer Stunde",
    "attributes": [
        {"label": "", "value": "1.380 €"},
        {"label": "", "value": "27,83 m²"},
        {"label": "", "value": "1 Zi."},
    ],
    "realEstateType": "apartmentrent",
}

SEARCH_RESPONSE = {
    "totalResults": 8524,
    "pageSize": 50,
    "pageNumber": 1,
    "numberOfPages": 171,
    "resultListItems": [
        {"type": "EXPOSE_RESULT", "item": SEARCH_ITEM},
        {"type": "AD", "item": {}},  # non-listing rows are ignored
    ],
}

EXPOSE_RESPONSE = {
    "header": {"id": "169446368", "title": "Beschreibung", "realEstateType": "apartmentrent"},
    "sections": [
        {
            "type": "TOP_ATTRIBUTES",
            "attributes": [
                {"label": "Kaltmiete", "text": "1.380 €"},
                {"label": "Zimmer", "text": "1"},
                {"label": "Wohnfläche", "text": "27,83 m²"},
            ],
        },
        {"type": "TEXT_AREA", "title": "Objektbeschreibung", "text": "Schönes Zimmer."},
        {"type": "MAP", "addressLine1": "Roedernallee 118H", "addressLine2": "13437 Berlin"},
    ],
}


class TestParseGermanNumber:
    def test_thousands_and_decimal(self):
        assert parse_german_number("1.380,50 €") == 1380.5

    def test_decimal_comma(self):
        assert parse_german_number("27,83 m²") == 27.83

    def test_plain_integer(self):
        assert parse_german_number("1 Zi.") == 1.0

    def test_no_number(self):
        assert parse_german_number("k. A.") is None
        assert parse_german_number(None) is None


class TestListing:
    def test_parses_price_space_rooms_by_unit(self):
        listing = Listing.from_api(SEARCH_ITEM)
        assert listing.price == 1380.0
        assert listing.currency == "EUR"
        assert listing.living_space == 27.83
        assert listing.rooms == 1.0

    def test_builds_expose_url_and_keeps_raw(self):
        listing = Listing.from_api(SEARCH_ITEM)
        assert listing.url == "https://www.immobilienscout24.de/expose/169446368"
        assert listing.address.latitude == 52.58927
        assert listing.is_new is True
        assert listing.raw == SEARCH_ITEM


class TestSearchResult:
    def test_parses_pagination_and_skips_non_listings(self):
        result = SearchResult.from_api(SEARCH_RESPONSE)
        assert result.total_results == 8524
        assert result.number_of_pages == 171
        assert len(result) == 1  # the AD row is skipped
        assert result.listings[0].id == "169446368"

    def test_is_iterable(self):
        result = SearchResult.from_api(SEARCH_RESPONSE)
        assert [listing.id for listing in result] == ["169446368"]


class TestExpose:
    def test_extracts_price_rooms_space_and_description(self):
        expose = Expose.from_api(EXPOSE_RESPONSE)
        assert expose.id == "169446368"
        assert expose.price == 1380.0
        assert expose.rooms == 1.0
        assert expose.living_space == 27.83
        assert expose.description == "Schönes Zimmer."
        assert expose.address == "Roedernallee 118H 13437 Berlin"
        assert expose.attributes["Kaltmiete"] == "1.380 €"
