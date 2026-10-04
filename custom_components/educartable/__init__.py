"""Intégration Educartable (non officielle, lecture seule)."""
from __future__ import annotations

from datetime import date
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EducartableApiError, EducartableAuthError, EducartableClient
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


class EducartableCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Récupère les données Educartable."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.client = EducartableClient(
            async_get_clientsession(hass), entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD]
        )
        self._parent_id: int | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if self._parent_id is None:
                self._parent_id = await self.client.async_get_parent_id()
            pid = self._parent_id
            return {
                "pupils": await self.client.async_get_pupils(pid),
                "lessons": await self.client.async_get_lessons(pid, date.today().isoformat()),
                "messages": await self.client.async_get_messages(pid),
            }
        except EducartableAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except EducartableApiError as err:
            raise UpdateFailed(str(err)) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = EducartableCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
