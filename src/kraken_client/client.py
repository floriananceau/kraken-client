import time
import hashlib
import hmac
import base64
import urllib.parse
import binascii
from typing import Optional, Dict, Any

import requests


class InvalidSecret(Exception):
    """Raised when the API secret is invalid."""

    pass


class KrakenAPIError(Exception):
    """Raised when there is an error with the Kraken API response."""

    pass


class Client:
    API_URL = "https://api.kraken.com"
    PUBLIC_PATH = "/0/public/"
    PRIVATE_PATH = "/0/private/"

    def __init__(
        self, api_key: str = "", api_secret: str = "", otp: Optional[str] = None
    ):
        """
        Initializes the KrakenAPI client.

        Args:
            api_key (str): Your Kraken API key.
            api_secret (str): Your Kraken API secret (Base64 encoded).
            otp (Optional[str]): Optional one-time password for two-factor authentication.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.otp = otp

        # Validate and decode the API secret
        try:
            base64.b64decode(self.api_secret)
        except binascii.Error as e:
            raise InvalidSecret(
                "Invalid API secret. Please provide a valid base64-encoded secret."
            ) from e

        self.session = requests.Session()

    @staticmethod
    def _get_nonce() -> str:
        """
        Generates a nonce required by Kraken for private API calls.

        Returns:
            str: A string representing the nonce (milliseconds since epoch).
        """
        return str(int(time.time() * 1000))

    def _sign_message(self, url_path: str, data: Dict[str, Any]) -> str:
        """
        Signs the message using HMAC-SHA512 encryption and the API secret.

        Args:
            url_path (str): The Kraken API endpoint path.
            data (Dict[str, Any]): The request payload.

        Returns:
            str: The API-Sign header value.
        """
        postdata = urllib.parse.urlencode(data)
        message = (str(data["nonce"]) + postdata).encode()
        url_path_encoded = url_path.encode()

        # Combine path and hash the message
        sha256_message = hashlib.sha256(message).digest()
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            url_path_encoded + sha256_message,
            hashlib.sha512,
        )
        return base64.b64encode(signature.digest()).decode()

    def _request(
        self, method: str, url_path: str, data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Sends a request to the Kraken API.

        Args:
            method (str): HTTP method (GET or POST).
            url_path (str): The API endpoint path.
            data (Optional[Dict[str, Any]]): Optional request data.

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            KrakenAPIError: If the request fails or Kraken returns an error.
        """
        url = f"{self.API_URL}{url_path}"
        headers = {}

        if data is None:
            data = {}

        # Apply authentication if the endpoint is private
        if "/private/" in url_path:
            data["nonce"] = self._get_nonce()
            if self.otp:
                data["otp"] = self.otp

            headers["API-Key"] = self.api_key
            headers["API-Sign"] = self._sign_message(url_path, data)

        response = self.session.request(method, url, headers=headers, data=data)

        # Check if the response has any Kraken errors
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise KrakenAPIError(f"Kraken API request failed: {e}") from e

        return response

    def public(
        self, method_name: str, data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Calls a public Kraken API endpoint (no authentication required).

        Args:
            method_name (str): The API method name (e.g., 'Time', 'Assets').
            data (Optional[Dict[str, Any]]): Optional query parameters.

        Returns:
            requests.Response: The HTTP response object.
        """
        url_path = f"{self.PUBLIC_PATH}{method_name}"
        return self._request("GET", url_path, data)

    def private(
        self, method_name: str, data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Calls a private Kraken API endpoint (authentication required).

        Args:
            method_name (str): The API method name (e.g., 'Balance', 'TradeBalance').
            data (Optional[Dict[str, Any]]): Optional query parameters.

        Returns:
            requests.Response: The HTTP response object.
        """
        url_path = f"{self.PRIVATE_PATH}{method_name}"
        return self._request("POST", url_path, data)
