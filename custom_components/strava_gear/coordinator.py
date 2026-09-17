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
        
        gear_ids = []

        # Discover gear IDs from athlete profile (active shoes and bikes)
        try:
            ath_res = requests.get("https://www.strava.com/api/v3/athlete", headers=headers, timeout=10)
            if ath_res.status_code == 200:
                athlete = ath_res.json()
                for s in athlete.get("shoes", []) or []:
                    if s.get("id") and s["id"] not in gear_ids:
                        gear_ids.append(s["id"])
                for b in athlete.get("bikes", []) or []:
                    if b.get("id") and b["id"] not in gear_ids:
                        gear_ids.append(b["id"])
            else:
                _LOGGER.warning("Could not fetch athlete profile: HTTP %s (%s)", ath_res.status_code, ath_res.text)
        except Exception as e:
            _LOGGER.warning("Could not fetch athlete profile: %s", e)

        # Also discover gear IDs from recent activities (up to 200 activities to cover all seasons)
        try:
            act_res = requests.get("https://www.strava.com/api/v3/athlete/activities?per_page=200", headers=headers, timeout=10)
            if act_res.status_code == 200:
                for act in act_res.json() or []:
                    act_gid = act.get("gear_id")
                    if act_gid and act_gid not in gear_ids:
                        gear_ids.append(act_gid)
            else:
                _LOGGER.warning("Could not fetch recent activities for gear discovery: HTTP %s (%s)", act_res.status_code, act_res.text)
        except Exception as e:
            _LOGGER.warning("Could not fetch recent activities for gear discovery: %s", e)

        shoes = []
        bikes = []

        for gid in gear_ids:
            try:
                g_res = requests.get(f"https://www.strava.com/api/v3/gear/{gid}", headers=headers, timeout=5)
                if g_res.status_code == 200:
                    gj = g_res.json()
                    name = gj.get("name", "")
                    km = round(gj.get("distance", 0) / 1000.0, 1)
                    distance_m = gj.get("distance", 0)
                    converted_distance = gj.get("converted_distance")
                    brand = gj.get("brand_name") or ""
                    model = gj.get("model_name") or ""
                    nickname = gj.get("nickname") or ""
                    description = gj.get("description") or ""
                    primary = gj.get("primary", False)
                    retired = gj.get("retired", False)
                    resource_state = gj.get("resource_state")
                    frame_type = gj.get("frame_type")
                    weight = gj.get("weight")

                    notif_dist = gj.get("notification_distance")
                    try:
                        max_km = round(float(notif_dist), 1) if (notif_dist is not None and float(notif_dist) > 0) else None
                    except (ValueError, TypeError):
                        max_km = None

                    wear_pct = min(100.0, round((km / max_km) * 100.0, 1)) if max_km else None
                    remaining = max(0.0, round(max_km - km, 1)) if max_km else None
                    replacement_needed = (wear_pct >= 95.0) if wear_pct is not None else False

                    item_dict = {
                        "id": gid,
                        "name": name,
                        "brand": brand,
                        "model": model,
                        "nickname": nickname,
                        "description": description,
                        "distance_km": km,
                        "distance_meters": distance_m,
                        "converted_distance": converted_distance,
                        "notification_distance": max_km,
                        "max_km": max_km,
                        "remaining_km": remaining,
                        "wear_pct": wear_pct,
                        "primary": primary,
                        "retired": retired,
                        "resource_state": resource_state,
                        "frame_type": frame_type,
                        "weight": weight,
                        "strava_data": gj,
                    }

                    if gid.startswith("g"):
                        item_dict["gear_type"] = "shoe"
                        item_dict["replacement_needed"] = replacement_needed
                        shoes.append(item_dict)
                    elif gid.startswith("b"):
                        item_dict["gear_type"] = "bike"
                        item_dict["replacement_needed"] = replacement_needed
                        bikes.append(item_dict)
            except Exception as ex:
                _LOGGER.warning("Failed fetching gear %s: %s", gid, ex)

        return {"shoes": shoes, "bikes": bikes}

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._sync_fetch_gear)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Strava gear: {err}") from err
