import requests

class ImmoscoutAPI:
    BASE_URL = 'https://api.mobile.immobilienscout24.de/'
    USER_AGENT = 'ImmoScout_27.3_26.0_._iOS'

    def search():

        r = requests.post(
            ImmoscoutAPI.BASE_URL + 'search/list',
            params={
                'pricetype': 'calculatedtotalrent',
                'realestatetype': 'apartmentrent',
                'searchType': 'region',
                'geocodes': '/de/berlin/berlin',
                'pagenumber': 1
            }, headers={
                'user-agent': ImmoscoutAPI.USER_AGENT,
            }, json={
                'supportedREsultListType': [],
                'userData': {}
            }
        )

        return r

    def get(id: str):
        r = requests.get(
            ImmoscoutAPI.BASE_URL + 'expose/' + id,
            headers={
                'user-agent': ImmoscoutAPI.USER_AGENT,
            }
        )

        return r

r = ImmoscoutAPI.search()
print(r.json())
r = ImmoscoutAPI.get('164013264')
for a in range(3):
    print()
print(r.json())