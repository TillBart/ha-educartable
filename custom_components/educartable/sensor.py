"""Capteurs Educartable."""
from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MAX_ITEMS


def _clean(text: Any, size: int = 300) -> str:
    """Retire le HTML et tronque."""
    text = re.sub(r"<[^>]+>", " ", str(text or ""))
    return re.sub(r"\s+", " ", text).strip()[:size]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            EducartableHomework(coordinator, entry),
            EducartableMessages(coordinator, entry),
            EducartableChildren(coordinator, entry),
        ]
    )


class _Base(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Educartable",
            manufacturer="Edumoov",
            entry_type=DeviceEntryType.SERVICE,
        )


class EducartableHomework(_Base):
    _attr_name = "Devoirs à venir"
    _attr_icon = "mdi:notebook-edit"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "homework")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["lessons"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        items = []
        for lesson in self.coordinator.data["lessons"][:MAX_ITEMS]:
            subject = lesson.get("subject")
            items.append(
                {
                    "date": lesson.get("date"),
                    "titre": lesson.get("title"),
                    "matiere": subject.get("name") if isinstance(subject, dict) else None,
                    "contenu": _clean(lesson.get("body")),
                }
            )
        return {"devoirs": items}


class EducartableMessages(_Base):
    _attr_name = "Messages et infos"
    _attr_icon = "mdi:email-newsletter"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "messages")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["messages"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        items = []
        for msg in self.coordinator.data["messages"][:MAX_ITEMS]:
            user = msg.get("user") or {}
            items.append(
                {
                    "date": msg.get("date") or msg.get("created"),
                    "type": msg.get("type"),
                    "titre": msg.get("title"),
                    "auteur": f"{user.get('firstname', '')} {user.get('name', '')}".strip(),
                    "contenu": _clean(msg.get("body")),
                }
            )
        return {"messages": items}


class EducartableChildren(_Base):
    _attr_name = "Enfants"
    _attr_icon = "mdi:school"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "children")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["pupils"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "enfants": [
                {
                    "prenom": p.get("firstname"),
                    "classe": (p.get("classroom") or {}).get("name"),
                    "niveau": (p.get("grade") or {}).get("name"),
                    "enseignant": (p.get("classroom") or {}).get("teacher_name"),
                }
                for p in self.coordinator.data["pupils"]
            ]
        }
