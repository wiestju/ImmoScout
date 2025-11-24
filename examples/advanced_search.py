from immoscout import ImmoscoutClient
from immoscout.exceptions import ImmoscoutError
import json

def main():
    client = ImmoscoutClient()

    try:
        # Advanced search with multiple parameters
        print("Searching for 3+ room apartments in Berlin between 1000-2000 EUR...")
        results = client.search(
            region='/de/berlin/berlin',
            price_type='calculatedtotalrent',
            real_estate_type='apartmentrent',
            price_from=1000,
            price_to=2000,
            rooms_from=3,
            sorting="2" # Sort by latest
        )

        total_results = results.get('totalResults', 0)
        print(f"Found {total_results} listings.")

        if total_results > 0:
            first_hit = results.get('resultList', {}).get('result', [])[0]
            print("\nFirst listing details:")
            print(json.dumps(first_hit, indent=2))

    except ImmoscoutError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
