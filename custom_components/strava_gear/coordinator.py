"""DataUpdateCoordinator for Strava Gear."""
from datetime import timedelta
import logging
import requests

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REFRESH_TOKEN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

DEFAULT_GEAR_IDS = [
    'g22352222', 'g17506784', 'g17087160', 'g30608631', 'g22619110', 'g20131340',
    'b16216412', 'b10239940', 'b8554804'
]

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
        
        gear_ids = list(DEFAULT_GEAR_IDS)

        # Also try to discover gear IDs from athlete profile if available
        try:
            ath_res = requests.get("https://www.strava.com/api/v3/athlete", headers=headers, timeout=10)
            if ath_res.status_code == 200:
                athlete = ath_res.json()
                for s in athlete.get("shoes", []):
                    if s.get("id") and s["id"] not in gear_ids:
                        gear_ids.append(s["id"])
                for b in athlete.get("bikes", []):
                    if b.get("id") and b["id"] not in gear_ids:
                        gear_ids.append(b["id"])
        except Exception as e:
            _LOGGER.warning("Could not fetch athlete profile: %s", e)

        shoes = []
        bikes = []

        for gid in gear_ids:
            try:
                g_res = requests.get(f"https://www.strava.com/api/v3/gear/{gid}", headers=headers, timeout=5)
                if g_res.status_code == 200:
                    gj = g_res.json()
                    name = gj.get("name", "")
                    km = round(gj.get("distance", 0) / 1000.0, 1)
                    brand = gj.get("brand_name") or ""
                    model = gj.get("model_name") or ""
                    primary = gj.get("primary", False)

                    if gid.startswith("g"):
                        name_lower = name.lower()
                        max_km = 1000.0 if "tr" in name_lower else (600.0 if "pulsar" in name_lower else 800.0)
                        wear_pct = min(100.0, round((km / max_km) * 100.0, 1))
                        remaining = max(0.0, round(max_km - km, 1))
                        shoes.append({
                            "id": gid,
                            "name": name,
                            "brand": brand,
                            "model": model,
                            "distance_km": km,
                            "max_km": max_km,
                            "remaining_km": remaining,
                            "wear_pct": wear_pct,
                            "primary": primary,
                            "replacement_needed": wear_pct >= 95.0
                        })
                    elif gid.startswith("b"):
                        bikes.append({
                            "id": gid,
                            "name": name,
                            "brand": brand,
                            "model": model,
                            "distance_km": km,
                            "primary": primary
                        })
            except Exception as ex:
                _LOGGER.warning("Failed fetching gear %s: %s", gid, ex)

        return {"shoes": shoes, "bikes": bikes}

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._sync_fetch_gear)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Strava gear: {err}") from err
