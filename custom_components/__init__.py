from __future__ import annotations

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CARD_URL, DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get("card_registered"):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    "/transperth_mobi",
                    hass.config.path("custom_components", DOMAIN, "www"),
                    False,
                )
            ]
        )
        frontend.add_extra_js_url(hass, CARD_URL)
        domain_data["card_registered"] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
