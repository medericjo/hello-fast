"""Thin async HTTP client for https://jsonplaceholder.typicode.com."""
from typing import Any, Dict, Optional

import httpx

from app.domain.exceptions import ExternalServiceError


class JsonPlaceholderClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET a path; returns parsed JSON, or None on 404."""
        try:
            response = await self._http.get(path, params=params)
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"JSONPlaceholder unreachable: {exc}") from exc

        if response.status_code == 404:
            return None
        if response.is_error:
            raise ExternalServiceError(
                f"JSONPlaceholder returned {response.status_code} for {path}"
            )
        return response.json()
