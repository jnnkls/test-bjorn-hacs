"""Sensors for Bjorn CyberViking."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BjornCoordinator
from .const import DOMAIN

# HINWEIS: Diese Schlüssel ("status", "targets_found", ...) sind ein
# sinnvoller Vorschlag, MÜSSEN aber ggf. an das tatsächliche JSON angepasst
# werden, das dein Bjorn unter STATUS_PATH zurückgibt. Schau dir dazu einmal
# `curl http://<bjorn-ip>:8000/status.json` an (oder den passenden Pfad,
# den du in const.py eingetragen hast) und passe value_fn entsprechend an.


@dataclass(frozen=True, kw_only=True)
class BjornSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any] = lambda data: None


SENSORS: tuple[BjornSensorDescription, ...] = (
    BjornSensorDescription(
        key="orchestrator_status",
        translation_key="orchestrator_status",
        name="Status",
        icon="mdi:robot",
        value_fn=lambda d: d.get("status") or d.get("bjornorch_status"),
    ),
    BjornSensorDescription(
        key="targets_found",
        translation_key="targets_found",
        name="Gefundene Ziele",
        icon="mdi:radar",
        value_fn=lambda d: d.get("targets_found") or d.get("alive_hosts"),
    ),
    BjornSensorDescription(
        key="vulnerabilities_found",
        translation_key="vulnerabilities_found",
        name="Gefundene Schwachstellen",
        icon="mdi:shield-alert",
        value_fn=lambda d: d.get("vulnerabilities_found"),
    ),
    BjornSensorDescription(
        key="credentials_cracked",
        translation_key="credentials_cracked",
        name="Geknackte Zugangsdaten",
        icon="mdi:key-alert",
        value_fn=lambda d: d.get("credentials_cracked") or d.get("cracked_pwd"),
    ),
    BjornSensorDescription(
        key="files_stolen",
        translation_key="files_stolen",
        name="Erbeutete Dateien",
        icon="mdi:file-download",
        value_fn=lambda d: d.get("files_stolen") or d.get("data_stolen"),
    ),
    BjornSensorDescription(
        key="zombies",
        translation_key="zombies",
        name="Zombie-Hosts",
        icon="mdi:skull",
        value_fn=lambda d: d.get("zombies"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: BjornCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BjornSensor(coordinator, entry, description) for description in SENSORS
    )


class BjornSensor(CoordinatorEntity[BjornCoordinator], SensorEntity):
    """Ein einzelner Key-Wert von Bjorn."""

    entity_description: BjornSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BjornCoordinator,
        entry: ConfigEntry,
        description: BjornSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Bjorn CyberViking",
            manufacturer="infinition",
            model="Bjorn",
        )

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data.status or {})

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None
