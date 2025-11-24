from immoscout import ImmoscoutClient
from immoscout.exceptions import ImmoscoutError, NotFoundError

def main():
    client = ImmoscoutClient()

    try:
        # Get a specific expose by ID
        expose_id = '164013264'
        print(f"Fetching expose {expose_id}...")
        
        expose_data = client.get_expose(expose_id)
        
        # Extract key information
        expose = expose_data.get('expose', {})
        
        print("\n=== Expose Details ===")
        print(f"Title: {expose.get('title')}")
        print(f"Address: {expose.get('address', {}).get('description')}")
        print(f"Price: {expose.get('price', {}).get('value')} EUR")
        print(f"Rooms: {expose.get('numberOfRooms')}")
        print(f"Living Space: {expose.get('livingSpace')} m²")
        
        # Print description if available
        description = expose.get('descriptionNote')
        if description:
            print(f"\nDescription:\n{description[:200]}...")  # First 200 chars

    except NotFoundError:
        print(f"Expose {expose_id} not found. Please use a valid ID from search results.")
    except ImmoscoutError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
