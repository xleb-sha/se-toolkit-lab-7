"""LMS API client for the Telegram bot.

Provides a clean interface to the LMS backend with proper error handling.
"""

import httpx
from typing import Any


class LMSClient:
    """Client for the LMS backend API.

    All API calls use Bearer token authentication.
    """

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS backend (e.g., http://localhost:42002).
            api_key: API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> list[dict[str, Any]]:
        """Get all items (labs and tasks) from the backend.

        Returns:
            List of items.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Get pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of pass rate records per task.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get(
            "/analytics/pass-rates",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "LMSClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


def create_lms_client(base_url: str, api_key: str) -> LMSClient:
    """Create an LMS client instance.

    Args:
        base_url: Base URL of the LMS backend.
        api_key: API key for authentication.

    Returns:
        Configured LMSClient instance.
    """
    return LMSClient(base_url, api_key)
