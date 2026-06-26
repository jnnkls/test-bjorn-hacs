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

# Diese Werte werden in api.py aus /netkb_data_json und /list_credentials
# zusammengerechnet (siehe _normalize_rows / _count_vulnerabilities dort).
# Falls deine Bjorn-Version andere Spaltennamen in der netkb verwendet,
# musst du api.py entsprechend anpassen.


@dataclass(frozen=True, kw_only=True)
class BjornSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any] = lambda data: None


SENSORS: tuple[BjornSensorDescription, ...] = (
    BjornSensorDescription(
        key="targets_found",
        translation_key="targets_found",
        name="Gefundene Ziele",
        icon="mdi:radar",
        value_fn=lambda d: d.get("targets_found"),
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
        value_fn=lambda d: d.get("credentials_cracked"),
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
        return self.entity_description.value_fn(self.coordinator.data.stats or {})

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None
