"""Minimal HTTP client to talk to a Bjorn CyberViking web interface."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

import aiohttp
import async_timeout

from .const import CREDENTIALS_PATH, NETKB_PATH, SCREEN_IMAGE_PATH

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10
NO_CACHE_HEADERS = {"Cache-Control": "no-cache", "Pragma": "no-cache"}

# Matcht jeden <tbody>...</tbody> Block der HTML-Antwort von /list_credentials
_TBODY_RE = re.compile(r"<tbody>(.*?)</tbody>", re.DOTALL | re.IGNORECASE)
_TR_RE = re.compile(r"<tr>", re.IGNORECASE)


@dataclass
class BjornData:
    """Container for everything we pull from Bjorn."""

    online: bool = False
    stats: dict[str, Any] = field(default_factory=dict)
    screen_image: bytes | None = None


class BjornApiError(Exception):
    """Raised when talking to Bjorn fails."""


def _count_credentials(html: str) -> int:
    """list_credentials liefert HTML-Tabellen (eine pro Dienst: ssh, ftp,
    smb, sql, rdp, telnet). Wir zählen einfach alle <tr>-Zeilen innerhalb
    der <tbody>-Blöcke - das sind die tatsächlich geknackten Zugangsdaten."""
    total = 0
    for tbody in _TBODY_RE.findall(html):
        total += len(_TR_RE.findall(tbody))
    return total


class BjornApiClient:
    """Talks to the Bjorn web interface (port 8000 by default)."""

    def __init__(self, host: str, port: int, session: aiohttp.ClientSession) -> None:
        self._base_url = f"http://{host}:{port}"
        self._session = session

    async def _get_text(self, path: str) -> str | None:
        async with async_timeout.timeout(TIMEOUT):
            resp = await self._session.get(
                f"{self._base_url}{path}", headers=NO_CACHE_HEADERS
            )
            if resp.status != 200:
                _LOGGER.debug("Bjorn %s antwortete mit HTTP %s", path, resp.status)
                return None
            return await resp.text()

    async def async_get_data(self) -> BjornData:
        """Fetch netkb + credentials + current screen image from Bjorn."""
        data = BjornData()

        # 1) Network Knowledge Base -> bekannte Hosts und offene Ports
        # Echtes Format: {"ips": [...], "ports": {ip: [...]}, "actions": [...]}
        try:
            raw = await self._get_text(NETKB_PATH)
            if raw:
                netkb = json.loads(raw)
                data.online = True
                ips = netkb.get("ips", [])
                ports = netkb.get("ports", {})
                data.stats["targets_found"] = len(ips)
                data.stats["open_ports_total"] = sum(
                    len([p for p in plist if p]) for plist in ports.values()
                )
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Konnte Bjorn netkb_data_json nicht laden: %s", err)
        except (ValueError, TypeError) as err:
            _LOGGER.debug("netkb_data_json war kein gültiges JSON: %s", err)

        # 2) Geknackte Zugangsdaten -> kommt als HTML, nicht als JSON!
        try:
            html = await self._get_text(CREDENTIALS_PATH)
            if html is not None:
                data.stats["credentials_cracked"] = _count_credentials(html)
                data.online = True
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Konnte Bjorn list_credentials nicht laden: %s", err)

        # 3) Aktuelles Bildschirmfoto (die "animierte" Figur)
        try:
            async with async_timeout.timeout(TIMEOUT):
                resp = await self._session.get(
                    f"{self._base_url}{SCREEN_IMAGE_PATH}", headers=NO_CACHE_HEADERS
                )
                if resp.status == 200:
                    data.screen_image = await resp.read()
                    data.online = True
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Konnte Bjorn-Bildschirmfoto nicht laden: %s", err)

        if not data.online:
            raise BjornApiError(
                f"Bjorn unter {self._base_url} nicht erreichbar "
                "(netkb_data_json, list_credentials und screen.png haben "
                "alle nicht geantwortet)."
            )

        return data
