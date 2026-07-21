# User guide

## Searching

`search()` returns a [`SearchResult`][immoscout.models.SearchResult] of typed
[`Listing`][immoscout.models.Listing] objects. `region` can be a geocode path *or* a plain
place name (auto-resolved for you):

```python
from immoscout import ImmoscoutClient

client = ImmoscoutClient()
result = client.search(region="Berlin", price_max=1200, rooms_min=2)

print(result.total_results, "results")
for listing in result.listings[:5]:
    print(listing.title)
    print(f"  {listing.price:.0f} {listing.currency} · {listing.rooms:g} rooms · {listing.living_space:g} m²")
    print(f"  {listing.address.line} — {listing.url}")
```

Every object keeps the untouched API payload on `.raw`.

## Filters

Build a reusable, validated query with [`SearchFilter`][immoscout.filters.SearchFilter]:

```python
from immoscout import RealEstateType, SearchFilter

query = SearchFilter(
    region="/de/bayern/muenchen",
    real_estate_type=RealEstateType.APARTMENT_RENT,
    price_min=800,
    price_max=1500,
    rooms_min=2,
    living_space_min=50,
)
result = client.search(query)
```

Ranges are open-ended too: `price_max=1000` alone means "up to 1000".

## Pagination

`search_all()` walks every result page transparently (one request per page). Cap it to stay
gentle:

```python
for listing in client.search_all(query, max_pages=3):
    print(listing.price, listing.title)
```

## Counting

Only need the number of matches? `count()` skips fetching listings entirely:

```python
client.count(region="Berlin", price_max=1000, rooms_min=2)   # -> e.g. 2527
```

## Finding a region

Don't guess geocode paths — look them up:

```python
for geo in client.suggest_regions("münchen"):
    print(geo.label, geo.region, geo.type)
# München            /de/bayern/muenchen         city
# München (Kreis)    /de/bayern/muenchen-kreis   district
```

## Expose details

```python
expose = client.get_expose("169446368")
print(expose.title, expose.price, expose.rooms, expose.living_space)
print(expose.address)
print(expose.attributes)   # {"Wohnungstyp": "Etagenwohnung", "Etage": "2 von 4", ...}
print(expose.description)
```

## Errors

All exceptions derive from [`ImmoscoutError`][immoscout.exceptions.ImmoscoutError]:

```python
from immoscout import NotFoundError, RateLimitError

try:
    client.get_expose("does-not-exist")
except NotFoundError:
    ...
except RateLimitError:
    ...  # back off — ImmoScout is throttling you
```
