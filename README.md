# Immoscout API Wrapper

[![PyPI version](https://badge.fury.io/py/immoscout.svg)](https://badge.fury.io/py/immoscout)
[![Tests](https://github.com/wiestju/immoscout/actions/workflows/tests.yml/badge.svg)](https://github.com/wiestju/immoscout/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust, unofficial Python API wrapper for ImmobilienScout24. This library allows you to easily search for real estate listings and retrieve detailed expose information programmatically.

## Features

- 🔍 **Advanced Search**: Filter by region, price type, real estate type, and more.
- 📄 **Detailed Exposes**: Fetch full details for any listing ID.
- 🚀 **Performance**: Built on `requests.Session` for connection pooling and faster requests.
- 🛡️ **Error Handling**: Custom exceptions for clean error management.
- 📦 **Type Hinted**: Fully typed for excellent IDE support and autocompletion.

## Installation

Install the package via pip:

```bash
pip install immoscout
```

## Quick Start

Here's how to get started in just a few lines of code:

```python
from immoscout import ImmoscoutClient
from immoscout.exceptions import ImmoscoutError

# Initialize the client
client = ImmoscoutClient()

try:
    # 1. Search for apartments in Berlin
    print("Searching for apartments...")
    results = client.search(
        region='/de/berlin/berlin',
        price_type='calculatedtotalrent',
        real_estate_type='apartmentrent'
    )
    
    print(f"Found {results.get('totalResults', 0)} results.")

    # 2. Get details for a specific listing (Expose)
    # Replace with a valid ID from your search results
    expose_id = '123456789' 
    expose = client.get_expose(expose_id)
    
    print(f"Expose Title: {expose.get('expose', {}).get('title')}")

except ImmoscoutError as e:
    print(f"An error occurred: {e}")
```

## Advanced Usage

### Customizing the Client

You can customize the `User-Agent` if needed:

```python
client = ImmoscoutClient(user_agent='MyCustomBot/1.0')
```

### Pagination

The search method supports pagination:

```python
# Get page 2
results_page_2 = client.search(
    region='/de/berlin/berlin',
    page_number=2
)
```

### Custom Search Parameters

You can pass any additional parameters supported by the Immoscout API as keyword arguments:

```python
results = client.search(
    region='/de/berlin/berlin',
    price_from=500,
    price_to=1000,
    rooms_from=2
)
```

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/immoscout.git
   cd immoscout
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Disclaimer

This is an unofficial wrapper and is not affiliated with, endorsed by, or connected to ImmobilienScout24. Use responsibly and in accordance with their Terms of Service.
