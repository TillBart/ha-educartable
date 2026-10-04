"""Client minimal (lecture seule) pour l'API Educartable Familles.

API non officielle : elle peut changer sans préavis.
"""
from __future__ import annotations

import time
from typing import Any

import aiohttp

from .const import API_URL, AUTH_URL, CLIENT_ID


class EducartableAuthError(Exception):
    """Identifiants refusés."""


class EducartableApiError(Exception):
    """Erreur de communication avec Educartable."""


class EducartableClient:
    """Client Educartable."""

    def __init__(self, session: aiohttp.ClientSession, email: str, password: str) -> None:
        self._session = session
        self._email = email
        self._password = password
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0.0

    async def _token_request(self, data: dict[str, str]) -> None:
        try:
            async with self._session.post(
                AUTH_URL,
                data={"client_id": CLIENT_ID, "scope": "openid", **data},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                payload = await resp.json(content_type=None)
                if resp.status in (400, 401):
                    raise EducartableAuthError(payload.get("error_description", "auth"))
                if resp.status != 200:
                    raise EducartableApiError(f"Auth HTTP {resp.status}")
        except aiohttp.ClientError as err:
            raise EducartableApiError(str(err)) from err

        self._access_token = payload["access_token"]
        self._refresh_token = payload.get("refresh_token")
        self._expires_at = time.time() + int(payload.get("expires_in", 300))

    async def async_login(self) -> None:
        """Connexion par email + mot de passe."""
        await self._token_request(
            {"grant_type": "password", "username": self._email, "password": self._password}
        )

    async def _ensure_token(self) -> None:
        if self._access_token and time.time() < self._expires_at - 60:
            return
        if self._refresh_token:
            try:
                await self._token_request(
                    {"grant_type": "refresh_token", "refresh_token": self._refresh_token}
                )
                return
            except EducartableAuthError:
                pass
        await self.async_login()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        await self._ensure_token()
        for attempt in (1, 2):
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Accept": "application/json, text/plain, */*",
            }
            try:
                async with self._session.get(
                    f"{API_URL}/{path}",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 401 and attempt == 1:
                        self._access_token = None
                        await self.async_login()
                        continue
                    if resp.status == 401:
                        raise EducartableAuthError("401")
                    if resp.status != 200:
                        raise EducartableApiError(f"HTTP {resp.status} sur {path}")
                    return await resp.json(content_type=None)
            except aiohttp.ClientError as err:
                raise EducartableApiError(str(err)) from err

    async def async_get_parent_id(self) -> int:
        data = await self._get("educore/users/me", {"light": 1})
        return int(data["data"]["id"])

    async def async_get_pupils(self, parent_id: int) -> list[dict[str, Any]]:
        data = await self._get(f"educore/parent/{parent_id}/pupils")
        return data.get("data", [])

    async def async_get_lessons(self, parent_id: int, start: str, limit: int = 30) -> list[dict[str, Any]]:
        data = await self._get(
            f"educartable/parent/{parent_id}/messages",
            {"type": "lesson", "sort": "date", "direction": "asc", "start": start, "limit": limit},
        )
        return data.get("data", [])

    async def async_get_messages(self, parent_id: int, limit: int = 30) -> list[dict[str, Any]]:
        data = await self._get(
            f"educartable/parent/{parent_id}/messages",
            {
                "type": "info,event,alert,meeting,advert",
                "sort": "visibility",
                "direction": "desc",
                "limit": limit,
            },
        )
        return data.get("data", [])
