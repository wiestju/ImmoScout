from immoscout import ImmoscoutClient
from immoscout.exceptions import ImmoscoutError

def main():
    client = ImmoscoutClient()

    try:
        # Search for houses for sale in Munich
        print("Searching for houses for sale in Munich...")
        results = client.search(
            region='/de/bayern/muenchen',
            price_type='buyprice',
            real_estate_type='housebuy',
            price_from=300000,
            price_to=800000,
            rooms_from=4
        )

        total_results = results.get('totalResults', 0)
        print(f"Found {total_results} houses.")

        # Display first 5 results
        result_list = results.get('resultList', {}).get('result', [])
        for i, listing in enumerate(result_list[:5], 1):
            print(f"\n{i}. {listing.get('title')}")
            print(f"   ID: {listing.get('id')}")
            print(f"   Price: {listing.get('price', {}).get('value')} EUR")
            print(f"   Rooms: {listing.get('numberOfRooms')}")

    except ImmoscoutError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
