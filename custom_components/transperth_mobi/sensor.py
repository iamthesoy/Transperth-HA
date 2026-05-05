from __future__ import annotations

from datetime import timedelta
from typing import Any, Literal
import logging
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .const import ATTR_DEPARTURES, CONF_SCAN_INTERVAL, CONF_STOP_ID, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

SLOT_COUNT = 5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    stop_id = str(entry.data[CONF_STOP_ID])
    scan_interval = int(entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    session = async_get_clientsession(hass)

    async def _async_update_data() -> dict[str, Any]:
        url = f"https://136213.mobi/RealTime/RealTimeStopResults.aspx?SN={stop_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-AU,en;q=0.9",
            "Referer": "https://136213.mobi/",
        }
        try:
            resp = await session.get(url, headers=headers, allow_redirects=True, timeout=20)
            if resp.status >= 400:
                raise UpdateFailed(f"HTTP {resp.status} from {resp.url}")
            body = await resp.text()
            departures = _parse_departures(body)
            return {"departures": departures}
        except Exception as err:
            raise UpdateFailed(f"Error fetching stop {stop_id}: {err}") from err

    coordinator: DataUpdateCoordinator[dict[str, Any]] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"transperth_mobi_{stop_id}",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    device_info = _device_info(entry, stop_id)
    entities: list[SensorEntity] = [TransperthMobiSensor(entry, coordinator, device_info)]

    for slot in range(1, SLOT_COUNT + 1):
        entities.append(
            TransperthMobiSlotSensor(entry, coordinator, device_info, slot, "route_number")
        )
        entities.append(TransperthMobiSlotSensor(entry, coordinator, device_info, slot, "eta"))
        entities.append(
            TransperthMobiSlotSensor(entry, coordinator, device_info, slot, "destination")
        )

    async_add_entities(entities)


def _device_info(entry: ConfigEntry, stop_id: str) -> DeviceInfo:
    name = str(entry.data.get(CONF_NAME, f"Transperth Stop {stop_id}"))
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer="Transperth",
        model=f"Stop {stop_id}",
        configuration_url=f"https://136213.mobi/RealTime/RealTimeStopResults.aspx?SN={stop_id}",
    )


class TransperthMobiSensor(CoordinatorEntity[DataUpdateCoordinator[dict[str, Any]]], SensorEntity):
    _attr_icon = "mdi:bus-clock"

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: DataUpdateCoordinator[dict[str, Any]],
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        stop_id = str(entry.data[CONF_STOP_ID])
        self._attr_unique_id = f"transperth_mobi_{stop_id}"
        self._attr_name = entry.data.get(CONF_NAME, f"Transperth Stop {stop_id}")
        self._stop_id = stop_id
        self._attr_device_info = device_info

    @property
    def native_value(self) -> str:
        departures = self.coordinator.data.get("departures", [])
        if not departures:
            return "No departures"
        first = departures[0]
        if first.get("minutes") is not None:
            return f"{first['route']} in {first['minutes']} min"
        return f"{first['route']} scheduled {first.get('time', '')}".strip()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "stop_id": self._stop_id,
            ATTR_DEPARTURES: self.coordinator.data.get("departures", []),
        }


class TransperthMobiSlotSensor(CoordinatorEntity[DataUpdateCoordinator[dict[str, Any]]], SensorEntity):
    """One of the next N departures: route number, ETA text, or destination."""

    _attr_icon = "mdi:bus-clock"

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: DataUpdateCoordinator[dict[str, Any]],
        device_info: DeviceInfo,
        slot: int,
        field: Literal["route_number", "eta", "destination"],
    ) -> None:
        super().__init__(coordinator)
        stop_id = str(entry.data[CONF_STOP_ID])
        self._slot = slot
        self._field = field
        self._attr_unique_id = f"transperth_mobi_{stop_id}_next_{slot}_{field}"
        labels = {
            "route_number": f"Next route {slot} number",
            "eta": f"Next route {slot} ETA",
            "destination": f"Next route {slot} destination",
        }
        self._attr_name = labels[field]
        self._attr_device_info = device_info

    def _departure_at_slot(self) -> dict[str, Any] | None:
        deps = self.coordinator.data.get("departures") or []
        idx = self._slot - 1
        if idx < 0 or idx >= len(deps):
            return None
        return deps[idx]

    @property
    def native_value(self) -> str:
        dep = self._departure_at_slot()
        if dep is None:
            return STATE_UNAVAILABLE

        if self._field == "route_number":
            return str(dep.get("route") or STATE_UNKNOWN)

        if self._field == "destination":
            return str(dep.get("destination") or STATE_UNKNOWN)

        # eta
        minutes = dep.get("minutes")
        if minutes is not None:
            return f"{minutes} min"
        if dep.get("scheduled_only") and dep.get("time"):
            return f"scheduled {dep['time']}"
        if dep.get("time"):
            return str(dep["time"])
        return STATE_UNKNOWN


def _parse_departures(html: str) -> list[dict[str, Any]]:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]*>", "\n", text)
    text = text.replace("&nbsp;", " ").replace("&#39;", "'").replace("&amp;", "&")

    lines = [line.strip() for line in text.replace("\r", "").split("\n") if line.strip()]
    by_blocks = _parse_route_blocks(lines)
    if by_blocks:
        return by_blocks

    flat = re.sub(r"\s+", " ", " ".join(lines)).strip()
    flat_pattern = re.compile(
        r"(\d{2,4})\s+To\s+(.+?)\s+(?:(\d+)\s*MIN)?\s*(\(sched\.\))?\s*(\d{1,2}:\d{2}(?:am|pm))",
        flags=re.IGNORECASE,
    )
    fallback: list[dict[str, Any]] = []
    for m in flat_pattern.finditer(flat):
        minutes = int(m.group(3)) if m.group(3) else None
        fallback.append(
            {
                "route": m.group(1).strip(),
                "destination": m.group(2).strip(),
                "minutes": minutes,
                "scheduled_only": bool(m.group(4)) or minutes is None,
                "time": m.group(5).strip(),
            }
        )
    return _dedup(fallback)


def _parse_route_blocks(lines: list[str]) -> list[dict[str, Any]]:
    route_re = re.compile(r"^\d{2,4}$")
    min_re = re.compile(r"(\d+)\s*MIN", flags=re.IGNORECASE)
    time_re = re.compile(r"\d{1,2}:\d{2}(?:am|pm)", flags=re.IGNORECASE)

    rows: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        if not route_re.match(lines[i]):
            i += 1
            continue

        if i + 1 >= len(lines) or not lines[i + 1].lower().startswith("to "):
            i += 1
            continue

        route = lines[i]
        destination = lines[i + 1][3:].strip()

        j = i + 2
        block: list[str] = []
        while j < len(lines):
            if route_re.match(lines[j]) and j + 1 < len(lines) and lines[j + 1].lower().startswith("to "):
                break
            block.append(lines[j])
            j += 1

        block_text = " ".join(block)
        min_match = min_re.search(block_text)
        time_match = time_re.search(block_text)
        minutes = int(min_match.group(1)) if min_match else None
        time_text = time_match.group(0) if time_match else ""

        if minutes is None and not time_text:
            i = j
            continue

        rows.append(
            {
                "route": route,
                "destination": destination,
                "minutes": minutes,
                "scheduled_only": "(sched.)" in block_text.lower() or minutes is None,
                "time": time_text,
            }
        )
        i = j

    return _dedup(rows)


def _dedup(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for d in rows:
        key = (d["route"], d["destination"], d.get("time", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out[:10]
