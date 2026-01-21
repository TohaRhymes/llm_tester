"""
Async-aware test client wrapper for sync test code.
"""
from __future__ import annotations

import anyio
import httpx

from app.main import app


class SyncASGIClient:
    """Minimal sync wrapper around httpx.AsyncClient(app=...)."""

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            return await client.request(method, url, **kwargs)

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async def runner() -> httpx.Response:
            return await self._request(method, url, **kwargs)

        return anyio.run(runner)

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)
