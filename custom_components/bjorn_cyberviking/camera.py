"""Camera entity showing Bjorn's live e-Paper screenshot on the dashboard."""
from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BjornCoordinator
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: BjornCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BjornScreenCamera(coordinator, entry)])


class BjornScreenCamera(CoordinatorEntity[BjornCoordinator], Camera):
    """Zeigt das aktuelle Bild des e-Paper-Displays (inkl. Bjorn-Figur)."""

    _attr_has_entity_name = True
    _attr_name = "Bildschirm"
    _attr_icon = "mdi:image-area"
    # Frontend soll das Bild im selben Takt pollen wie der Coordinator,
    # sonst zeigt die Karte ein veraltetes Bild.
    _attr_frame_interval = 5

    def __init__(self, coordinator: BjornCoordinator, entry: ConfigEntry) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry.entry_id}_screen"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Bjorn CyberViking",
            manufacturer="infinition",
            model="Bjorn",
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.screen_image
