from immoscout import ImmoscoutClient
from immoscout.exceptions import ImmoscoutError

def main():
    client = ImmoscoutClient()

    try:
        # Search with pagination - get multiple pages
        print("Fetching first 3 pages of results...")
        
        for page in range(1, 4):
            print(f"\n--- Page {page} ---")
            results = client.search(
                region='/de/berlin/berlin',
                price_type='calculatedtotalrent',
                real_estate_type='apartmentrent',
                page_number=page
            )
            
            total_results = results.get('totalResults', 0)
            result_list = results.get('resultList', {}).get('result', [])
            
            print(f"Total results: {total_results}")
            print(f"Results on this page: {len(result_list)}")
            
            # Print first listing from each page
            if result_list:
                first = result_list[0]
                print(f"First listing ID: {first.get('id')}")
                print(f"Title: {first.get('title')}")

    except ImmoscoutError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
