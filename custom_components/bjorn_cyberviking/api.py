"""Minimal HTTP client to talk to a Bjorn CyberViking web interface."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import aiohttp
import async_timeout

from .const import SCREEN_IMAGE_PATH, STATUS_PATH

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


@dataclass
class BjornData:
    """Container for everything we pull from Bjorn."""

    online: bool = False
    status: dict[str, Any] = field(default_factory=dict)
    screen_image: bytes | None = None


class BjornApiError(Exception):
    """Raised when talking to Bjorn fails."""


class BjornApiClient:
    """Talks to the Bjorn web interface (port 8000 by default)."""

    def __init__(self, host: str, port: int, session: aiohttp.ClientSession) -> None:
        self._base_url = f"http://{host}:{port}"
        self._session = session

    async def async_get_data(self) -> BjornData:
        """Fetch status + current screen image from Bjorn."""
        data = BjornData()

        # 1) Status-JSON (Key-Werte: Orchestrator-Status, Funde, etc.)
        try:
            async with async_timeout.timeout(TIMEOUT):
                resp = await self._session.get(f"{self._base_url}{STATUS_PATH}")
                if resp.status == 200:
                    data.status = await resp.json(content_type=None)
                    data.online = True
                else:
                    _LOGGER.debug(
                        "Bjorn status endpoint antwortete mit HTTP %s - "
                        "Pfad ggf. in const.STATUS_PATH anpassen.",
                        resp.status,
                    )
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Konnte Bjorn-Status nicht laden: %s", err)

        # 2) Aktuelles Bildschirmfoto (die "animierte" Figur)
        try:
            async with async_timeout.timeout(TIMEOUT):
                resp = await self._session.get(f"{self._base_url}{SCREEN_IMAGE_PATH}")
                if resp.status == 200:
                    data.screen_image = await resp.read()
                    data.online = True
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Konnte Bjorn-Bildschirmfoto nicht laden: %s", err)

        if not data.online:
            raise BjornApiError(
                f"Bjorn unter {self._base_url} nicht erreichbar "
                "(weder Status- noch Bild-Endpoint haben geantwortet)."
            )

        return data
