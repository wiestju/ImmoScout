"""Typed filters + auto-pagination across all result pages."""
from immoscout import ImmoscoutClient, RealEstateType, SearchFilter

client = ImmoscoutClient()

query = SearchFilter(
    region="/de/bayern/muenchen",
    real_estate_type=RealEstateType.APARTMENT_RENT,
    price_max=1500,
    rooms_min=2,
    living_space_min=50,
)

# search_all() transparently walks every page — cap it so we stay gentle.
count = 0
for listing in client.search_all(query, max_pages=3):
    count += 1
    print(f"{count:>3}. {listing.price:>6.0f} € · {listing.rooms:g} rm · {listing.title[:50]}")

print(f"\nCollected {count} listings across up to 3 pages.")
