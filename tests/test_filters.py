from immoscout.filters import RealEstateType, SearchFilter


class TestSearchFilter:
    def test_defaults_produce_core_params(self):
        params = SearchFilter().to_params()
        assert params["searchType"] == "region"
        assert params["geocodes"] == "/de/berlin/berlin"
        assert params["realestatetype"] == "apartmentrent"
        assert params["pagenumber"] == 1
        # no range filters unless requested
        assert "price" not in params
        assert "numberofrooms" not in params

    def test_price_range_both_bounds(self):
        assert SearchFilter(price_min=500, price_max=800).to_params()["price"] == "500.0-800.0"

    def test_open_ended_ranges(self):
        assert SearchFilter(living_space_min=50).to_params()["livingspace"] == "50.0-"
        assert SearchFilter(price_max=1000).to_params()["price"] == "-1000.0"

    def test_rooms_and_enum_type(self):
        params = SearchFilter(
            real_estate_type=RealEstateType.HOUSE_BUY, rooms_min=2, rooms_max=4
        ).to_params()
        assert params["realestatetype"] == "housebuy"
        assert params["numberofrooms"] == "2.0-4.0"

    def test_extra_passthrough(self):
        assert SearchFilter(extra={"foo": "bar"}).to_params()["foo"] == "bar"
