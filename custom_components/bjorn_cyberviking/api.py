"""Minimal HTTP client to talk to a Bjorn CyberViking web interface."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import aiohttp
import async_timeout

from .const import CREDENTIALS_PATH, NETKB_PATH, SCREEN_IMAGE_PATH

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10

# Keine Caches respektieren - wir wollen immer den aktuellen Stand
NO_CACHE_HEADERS = {"Cache-Control": "no-cache", "Pragma": "no-cache"}


@dataclass
class BjornData:
    """Container for everything we pull from Bjorn."""

    online: bool = False
    stats: dict[str, Any] = field(default_factory=dict)
    screen_image: bytes | None = None


class BjornApiError(Exception):
    """Raised when talking to Bjorn fails."""


def _normalize_rows(payload: Any) -> list[dict[str, Any]]:
    """netkb_data_json / list_credentials liefern je nach Version entweder
    direkt eine Liste von Dicts, oder ein Wrapper-Dict mit 'data'/'netkb'."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "netkb", "rows", "credentials"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def _truthy_alive(value: Any) -> bool:
    return str(value).strip() in ("1", "1.0", "True", "true", "yes")


def _count_vulnerabilities(row: dict[str, Any]) -> int:
    """Die Vulnerabilities-Spalte ist meist ein String mit z.B.
    kommagetrennten CVEs/Findings - wir zählen Einträge statt Zeichen."""
    raw = row.get("Vulnerabilities") or row.get("vulnerabilities")
    if not raw or str(raw).strip().lower() in ("", "none", "nan"):
        return 0
    return len([part for part in str(raw).split(",") if part.strip()])


class BjornApiClient:
    """Talks to the Bjorn web interface (port 8000 by default)."""

    def __init__(self, host: str, port: int, session: aiohttp.ClientSession) -> None:
        self._base_url = f"http://{host}:{port}"
        self._session = session

    async def _get_json(self, path: str) -> Any:
        async with async_timeout.timeout(TIMEOUT):
            resp = await self._session.get(
                f"{self._base_url}{path}", headers=NO_CACHE_HEADERS
            )
            if resp.status != 200:
                _LOGGER.debug("Bjorn %s antwortete mit HTTP %s", path, resp.status)
                return None
            return await resp.json(content_type=None)

    async def async_get_data(self) -> BjornData:
        """Fetch netkb + credentials + current screen image from Bjorn."""
        data = BjornData()

        # 1) Network Knowledge Base -> Hosts, offene Ports, Schwachstellen
        try:
            netkb = _normalize_rows(await self._get_json(NETKB_PATH))
            if netkb:
                data.online = True
            alive_hosts = [r for r in netkb if _truthy_alive(r.get("Alive"))]
            data.stats["targets_found"] = len(alive_hosts)
            data.stats["vulnerabilities_found"] = sum(
                _count_vulnerabilities(r) for r in netkb
            )
            data.stats["zombies"] = sum(
                1
                for r in netkb
                if str(r.get("Zombie", r.get("zombie", ""))).strip()
                in ("1", "1.0", "True", "true", "yes")
            )
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Konnte Bjorn netkb_data_json nicht laden: %s", err)

        # 2) Geknackte Zugangsdaten
        try:
            creds = _normalize_rows(await self._get_json(CREDENTIALS_PATH))
            data.stats["credentials_cracked"] = len(creds)
            if creds:
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
