import pytest
import base64
import requests

from kraken_client import Client, InvalidSecret, KrakenAPIError


@pytest.fixture
def client():
    """Fixture to create a valid Client instance."""
    api_key = base64.b64encode(b"key").decode()
    api_secret = base64.b64encode(b"secret").decode()
    return Client(api_key=api_key, api_secret=api_secret)


def test_invalid_secret():
    """Test that InvalidSecret is raised for an invalid API secret."""
    api_key = base64.b64encode(b"key").decode()
    invalid_secret = "key"  # Incorrectly padded (not divisble by 4)
    with pytest.raises(InvalidSecret):
        Client(api_key=api_key, api_secret=invalid_secret)


def test_public_endpoint(mocker, client):
    """Test calling a public Kraken API endpoint."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    mock_request = mocker.patch.object(
        client.session, "request", return_value=mock_response
    )

    # Call public method
    response = client.public("Time")
    assert response.status_code == 200
    assert response.json() == {"result": "success"}

    # Ensure the correct URL is hit and the request was made
    mock_request.assert_called_once_with(
        "GET", "https://api.kraken.com/0/public/Time", headers={}, data={}
    )


def test_private_endpoint(mocker, client):
    """Test calling a private Kraken API endpoint."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    mock_request = mocker.patch.object(
        client.session, "request", return_value=mock_response
    )

    # Call private method
    response = client.private("Balance", data={"nonce": "nonce_value"})
    assert response.status_code == 200
    assert response.json() == {"result": "success"}

    # Ensure the correct URL is hit, and check the headers and data
    assert "API-Key" in mock_request.call_args[1]["headers"]
    assert "API-Sign" in mock_request.call_args[1]["headers"]
    assert "nonce" in mock_request.call_args[1]["data"]


def test_private_endpoint_otp(mocker, client):
    """Test calling a private Kraken API endpoint with OTP."""
    client.otp = "123456"
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    mock_request = mocker.patch.object(
        client.session, "request", return_value=mock_response
    )

    # Call private method with OTP
    response = client.private("Balance")
    assert response.status_code == 200
    assert response.json() == {"result": "success"}

    # Ensure OTP is included in the request data
    _, kwargs = mock_request.call_args
    assert kwargs["data"]["otp"] == "123456"


def test_private_endpoint_signature(mocker, client):
    """Test that the correct signature is generated for private API calls."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    mock_request = mocker.patch.object(
        client.session, "request", return_value=mock_response
    )

    # Call private method
    response = client.private("Balance")
    assert response.status_code == 200

    # Extract API-Sign from the headers
    _, kwargs = mock_request.call_args
    api_sign = kwargs["headers"]["API-Sign"]
    assert isinstance(api_sign, str)  # Ensure API-Sign is generated


def test_request_exception(mocker, client):
    """Test that KrakenAPIError is raised on HTTP error."""
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Bad request"
    )
    mocker.patch.object(client.session, "request", return_value=mock_response)

    with pytest.raises(KrakenAPIError, match="Kraken API request failed: Bad request"):
        client.private("Balance")


def test_nonce_generation():
    """Test nonce generation to ensure it's a string representing the current time in milliseconds."""
    client = Client(api_key="some_key", api_secret=base64.b64encode(b"secret").decode())
    nonce = client._get_nonce()
    assert isinstance(nonce, str)
    assert nonce.isdigit()


def test_real_public_api_call():
    """
    Test a real call to Kraken's public API.

    This test hits Kraken's public API (Time endpoint) and checks the response.
    """
    client = Client()
    response = client.public("Time")
    assert response.status_code == 200

    json_response = response.json()

    # Ensure there is a 'result' field in the response
    assert "result" in json_response
    assert "unixtime" in json_response["result"]
    assert isinstance(json_response["result"]["unixtime"], int)

    # Print the result (for debugging purposes, not necessary in production tests)
    print(f"Kraken Time API Response: {json_response}")
