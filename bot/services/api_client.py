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

    def get_learners(self) -> list[dict[str, Any]]:
        """Get list of enrolled learners.

        Returns:
            List of learners.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict[str, Any]]:
        """Get score distribution for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of score distribution records.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get(
            "/analytics/scores",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def get_timeline(self, lab: str) -> list[dict[str, Any]]:
        """Get submissions per day timeline for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of timeline records.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get(
            "/analytics/timeline",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict[str, Any]]:
        """Get per-group scores and student counts for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of group records.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get(
            "/analytics/groups",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get top N learners by score for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").
            limit: Number of top learners to return.

        Returns:
            List of top learners.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get(
            "/analytics/top-learners",
            params={"lab": lab, "limit": limit},
        )
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict[str, Any]:
        """Get completion rate percentage for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Completion rate data.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.get(
            "/analytics/completion-rate",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict[str, Any]:
        """Trigger ETL sync to refresh data from autochecker.

        Returns:
            Sync result data.

        Raises:
            httpx.RequestError: If the request fails.
        """
        response = self._client.post("/pipeline/sync", json={})
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
