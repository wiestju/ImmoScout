import requests
from typing import Optional, Dict, Any
from .exceptions import RequestError, NotFoundError

class ImmoscoutClient:
    BASE_URL = 'https://api.mobile.immobilienscout24.de'
    DEFAULT_USER_AGENT = 'ImmoScout_27.3_26.0_._iOS'

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': user_agent
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Resource not found: {url}") from e
            raise RequestError(f"HTTP error occurred: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RequestError(f"Request failed: {e}") from e

    def search(self, 
               region: str = '/de/berlin/berlin',
               price_type: str = 'calculatedtotalrent',
               real_estate_type: str = 'apartmentrent',
               page_number: int = 1,
               **kwargs) -> Dict[str, Any]:
        """
        Search for real estate listings.
        
        Args:
            region: The region to search in (e.g., '/de/berlin/berlin').
            price_type: The type of price (e.g., 'calculatedtotalrent').
            real_estate_type: The type of real estate (e.g., 'apartmentrent').
            page_number: The page number to retrieve.
            **kwargs: Additional parameters to pass to the API.
        """
        params = {
            'pricetype': price_type,
            'realestatetype': real_estate_type,
            'searchType': 'region',
            'geocodes': region,
            'pagenumber': page_number
        }
        # Merge additional kwargs into params
        params.update(kwargs)

        payload = {
            'supportedREsultListType': [],
            'userData': {}
        }

        return self._request('POST', 'search/list', params=params, json=payload)

    def get_expose(self, expose_id: str) -> Dict[str, Any]:
        """
        Get details for a specific expose (listing).
        
        Args:
            expose_id: The ID of the expose to retrieve.
        """
        return self._request('GET', f'expose/{expose_id}')
