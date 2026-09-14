"""DataUpdateCoordinator for Strava Gear."""
from datetime import timedelta
import logging
import requests

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REFRESH_TOKEN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class StravaGearDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Strava gear data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client_id = entry.data[CONF_CLIENT_ID]
        self.client_secret = entry.data[CONF_CLIENT_SECRET]
        self.refresh_token = entry.data[CONF_REFRESH_TOKEN]
        self.access_token = entry.data.get("access_token")
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    def _sync_fetch_gear(self):
        """Fetch athlete gear from Strava."""
        # 1. Refresh token
        token_res = requests.post("https://www.strava.com/oauth/token", data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }, timeout=10)

        if token_res.status_code == 200:
            tj = token_res.json()
            self.access_token = tj["access_token"]
            self.refresh_token = tj.get("refresh_token", self.refresh_token)

        headers = {"Authorization": f"Bearer {self.access_token}"}
        ath_res = requests.get("https://www.strava.com/api/v3/athlete", headers=headers, timeout=10)
        if ath_res.status_code != 200:
            raise UpdateFailed(f"Failed to fetch Strava athlete: {ath_res.text}")

        athlete = ath_res.json()
        shoes = []
        for s in athlete.get("shoes", []):
            sid = s.get("id")
            g_res = requests.get(f"https://www.strava.com/api/v3/gear/{sid}", headers=headers, timeout=5)
            if g_res.status_code == 200:
                gj = g_res.json()
                km = round(gj.get("distance", 0) / 1000.0, 1)
                max_km = 1000.0 if "tr" in gj.get("name", "").lower() else (600.0 if "pulsar" in gj.get("name", "").lower() else 800.0)
                wear_pct = min(100.0, round((km / max_km) * 100.0, 1))
                remaining = max(0.0, round(max_km - km, 1))
                shoes.append({
                    "id": sid,
                    "name": gj.get("name"),
                    "brand": gj.get("brand_name"),
                    "model": gj.get("model_name"),
                    "distance_km": km,
                    "max_km": max_km,
                    "remaining_km": remaining,
                    "wear_pct": wear_pct,
                    "primary": gj.get("primary", False),
                    "replacement_needed": wear_pct >= 95.0
                })

        bikes = []
        for b in athlete.get("bikes", []):
            bid = b.get("id")
            g_res = requests.get(f"https://www.strava.com/api/v3/gear/{bid}", headers=headers, timeout=5)
            if g_res.status_code == 200:
                gj = g_res.json()
                km = round(gj.get("distance", 0) / 1000.0, 1)
                bikes.append({
                    "id": bid,
                    "name": gj.get("name"),
                    "brand": gj.get("brand_name"),
                    "model": gj.get("model_name"),
                    "distance_km": km,
                    "primary": gj.get("primary", False)
                })

        return {"shoes": shoes, "bikes": bikes}

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._sync_fetch_gear)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Strava gear: {err}") from err
