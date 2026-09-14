"""Config flow for Strava Gear."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REFRESH_TOKEN

class StravaGearConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Strava Gear", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_CLIENT_ID): int,
            vol.Required(CONF_CLIENT_SECRET): str,
            vol.Required(CONF_REFRESH_TOKEN): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)
