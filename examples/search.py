"""Basic search: find apartments to rent in Berlin under 1200 €/month."""
from immoscout import ImmoscoutClient

client = ImmoscoutClient()

result = client.search(region="/de/berlin/berlin", price_max=1200, rooms_min=2)
print(f"{result.total_results} results — showing {len(result)} from page {result.page_number}\n")

for listing in result.listings[:5]:
    print(f"{listing.title}")
    print(f"  {listing.price:.0f} {listing.currency} · {listing.rooms:g} rooms · {listing.living_space:g} m²")
    print(f"  {listing.address.line}")
    print(f"  {listing.url}\n")
