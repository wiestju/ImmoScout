"""Fetch full details for the first search result."""
from immoscout import ImmoscoutClient

client = ImmoscoutClient()

listing = client.search(region="/de/berlin/berlin").listings[0]
expose = client.get_expose(listing.id)

print(f"{expose.title}  ({expose.url})")
print(f"Price: {expose.price} € · Rooms: {expose.rooms} · Space: {expose.living_space} m²")
print(f"Address: {expose.address}\n")
print("Key facts:")
for label, value in list(expose.attributes.items())[:10]:
    print(f"  {label}: {value}")
print(f"\nDescription ({len(expose.description or '')} chars):")
print((expose.description or "")[:400])
