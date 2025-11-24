import sys
import os
import json

# Add the project root to the python path so we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from immoscout import ImmoscoutClient
from immoscout.exceptions import ImmoscoutError

def main():
    client = ImmoscoutClient()

    print("Searching for apartments in Berlin...")
    try:
        # Search for apartments in Berlin
        search_results = client.search(
            region='/de/berlin/berlin',
            price_type='calculatedtotalrent',
            real_estate_type='apartmentrent'
        )
        
        # Print the first result to verify structure
        # Note: The actual structure depends on the API response, 
        # but usually there is a list under 'searchResponseModel' -> 'resultlist.json' -> 'resultlistEntries'
        # or similar. For now, we just print the keys.
        print("Search successful!")
        print(f"Keys in response: {list(search_results.keys())}")
        
        # Try to get an ID from the search results to test get_expose
        # This part is a bit speculative on the response structure, 
        # so we'll just try to use the ID from the original main.py if we can't find one dynamically,
        # or just skip if the structure is complex.
        # For this test, let's use the ID from the user's original script: '164013264'
        test_id = '164013264'
        
        print(f"\nFetching details for expose {test_id}...")
        expose_details = client.get_expose(test_id)
        print("Expose details fetched successfully!")
        # print(json.dumps(expose_details, indent=2)) # Uncomment to see full details

    except ImmoscoutError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
