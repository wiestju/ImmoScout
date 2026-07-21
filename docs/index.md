# immoscout

A **typed, unofficial Python client for [ImmobilienScout24](https://www.immobilienscout24.de)** —
search real-estate listings, fetch expose details, and plug it all into AI agents.

Instead of a raw JSON blob, you get clean typed objects (`Listing`, `Expose`) — and a
built-in [MCP](https://modelcontextprotocol.io) server so assistants like Claude can search
real estate for you natively.

!!! tip "No captcha, no browser"
    It uses ImmobilienScout24's **mobile API**, which returns JSON directly — so there's no
    headless browser, no HTML scraping, and **no captcha to solve**. Where the website makes
    even human users pass captchas, the mobile endpoints just answer.

```bash
pip install immoscout
```

```python
from immoscout import ImmoscoutClient

client = ImmoscoutClient()
result = client.search(region="Berlin", price_max=1200, rooms_min=2)

for listing in result.listings[:5]:
    print(listing.price, listing.rooms, listing.living_space, listing.url)
```

!!! warning "Unofficial & responsible use"
    Not affiliated with ImmobilienScout24. It actively rate-limits and blocks automated
    traffic — keep the built-in timeouts/retries, be gentle, and use it for personal and
    educational purposes. See the project's `DISCLAIMER.md`.

## Where to next

- **[User guide](guide.md)** — searching, filters, pagination, exposes, regions, counting.
- **[AI agents (MCP)](mcp.md)** — run the MCP server and let Claude search for you.
- **[API reference](api.md)** — every class and method, generated from the source.
