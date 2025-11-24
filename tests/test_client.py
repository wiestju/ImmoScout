import pytest
from immoscout import ImmoscoutClient

def test_client_instantiation():
    client = ImmoscoutClient()
    assert client.session is not None
    assert "User-Agent" in client.session.headers

def test_client_custom_user_agent():
    custom_ua = "MyBot/1.0"
    client = ImmoscoutClient(user_agent=custom_ua)
    assert client.session.headers["User-Agent"] == custom_ua
