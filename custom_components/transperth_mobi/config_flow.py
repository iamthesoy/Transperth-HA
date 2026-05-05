from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME

from .const import CONF_SCAN_INTERVAL, CONF_STOP_ID, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN


class TransperthMobiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            stop_id = str(user_input[CONF_STOP_ID]).strip()
            if not stop_id.isdigit():
                errors[CONF_STOP_ID] = "invalid_stop_id"
            else:
                await self.async_set_unique_id(stop_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_STOP_ID: stop_id,
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_STOP_ID): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=600)
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
