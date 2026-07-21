import pytest
import responses

from immoscout import ImmoscoutClient, NotFoundError, RateLimitError, SearchResult
from immoscout.client import ImmoscoutClient as _C
from tests.test_models import EXPOSE_RESPONSE, SEARCH_RESPONSE

SEARCH_URL = f"{_C.BASE_URL}/search/list"


def _client():
    # no real waiting between retries during tests
    return ImmoscoutClient(max_retries=2, backoff=0)


class TestSearch:
    @responses.activate
    def test_search_returns_typed_result(self):
        responses.add(responses.POST, SEARCH_URL, json=SEARCH_RESPONSE, status=200)
        result = _client().search(region="/de/berlin/berlin", price_max=1200)
        assert isinstance(result, SearchResult)
        assert result.total_results == 8524
        assert result.listings[0].price == 1380.0

    @responses.activate
    def test_search_sets_a_timeout(self):
        responses.add(responses.POST, SEARCH_URL, json=SEARCH_RESPONSE, status=200)
        _client().search()
        # the outgoing request must carry a timeout (never hang forever)
        assert responses.calls[0].request.req_kwargs.get("timeout") == 15.0


class TestGetExpose:
    @responses.activate
    def test_get_expose_returns_typed(self):
        responses.add(
            responses.GET, f"{_C.BASE_URL}/expose/123", json=EXPOSE_RESPONSE, status=200
        )
        expose = _client().get_expose("123")
        assert expose.id == "169446368"
        assert expose.rooms == 1.0

    @responses.activate
    def test_404_raises_not_found(self):
        responses.add(responses.GET, f"{_C.BASE_URL}/expose/999", status=404)
        with pytest.raises(NotFoundError):
            _client().get_expose("999")


class TestSuggestRegions:
    @responses.activate
    def test_resolves_place_to_region_path(self):
        responses.add(
            responses.GET,
            f"{_C.BASE_URL}/geoautocomplete/v3/locations.json",
            json=[
                {"entity": {"type": "city", "id": "1276002059", "label": "München",
                            "geopath": {"uri": "/de/bayern/muenchen"}}},
            ],
            status=200,
        )
        regions = _client().suggest_regions("münchen")
        assert regions[0].label == "München"
        assert regions[0].region == "/de/bayern/muenchen"
        assert regions[0].type == "city"


class TestCount:
    @responses.activate
    def test_count_returns_total_only(self):
        responses.add(
            responses.GET, f"{_C.BASE_URL}/search/total", json={"totalResults": 42}, status=200
        )
        assert _client().count(region="/de/berlin/berlin", price_max=1000) == 42


class TestRegionAutoResolve:
    @responses.activate
    def test_plain_name_resolved_before_search(self):
        responses.add(
            responses.GET,
            f"{_C.BASE_URL}/geoautocomplete/v3/locations.json",
            json=[{"entity": {"label": "München", "geopath": {"uri": "/de/bayern/muenchen"}}}],
            status=200,
        )
        responses.add(responses.POST, SEARCH_URL, json=SEARCH_RESPONSE, status=200)
        _client().search(region="München")
        post = next(c for c in responses.calls if c.request.method == "POST")
        assert "muenchen" in post.request.url  # resolved geocode path was used

    @responses.activate
    def test_geocode_path_is_not_resolved(self):
        # a region that already looks like a path must not trigger autocomplete
        responses.add(responses.POST, SEARCH_URL, json=SEARCH_RESPONSE, status=200)
        _client().search(region="/de/berlin/berlin")
        assert all("geoautocomplete" not in c.request.url for c in responses.calls)


class TestRetriesAndRateLimit:
    @responses.activate
    def test_429_retries_then_raises_rate_limit(self):
        for _ in range(3):
            responses.add(responses.POST, SEARCH_URL, status=429)
        with pytest.raises(RateLimitError):
            _client().search()
        assert len(responses.calls) == 3  # 1 try + 2 retries

    @responses.activate
    def test_recovers_after_transient_500(self):
        responses.add(responses.POST, SEARCH_URL, status=500)
        responses.add(responses.POST, SEARCH_URL, json=SEARCH_RESPONSE, status=200)
        result = _client().search()
        assert result.total_results == 8524
        assert len(responses.calls) == 2
