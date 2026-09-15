"""Binary sensor platform for Strava Gear wear alerts."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for shoe in coordinator.data.get("shoes", []):
        entities.append(StravaShoeWearAlertBinarySensor(coordinator, entry, shoe["id"], shoe["name"]))
    async_add_entities(entities)

class StravaShoeWearAlertBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, gear_id, name):
        super().__init__(coordinator)
        self._gear_id = gear_id
        self._gear_name = name
        self._attr_name = f"Alerte Usure {name}"
        self._attr_unique_id = f"{entry.entry_id}_{gear_id}_wear_alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:alert-decagram"

    def _get_item(self):
        for s in self.coordinator.data.get("shoes", []):
            if s["id"] == self._gear_id:
                return s
        return {}

    @property
    def device_info(self) -> DeviceInfo:
        item = self._get_item()
        return DeviceInfo(
            identifiers={(DOMAIN, self._gear_id)},
            name=f"Chaussure {self._gear_name}",
            manufacturer=item.get("brand") or "Strava",
            model=item.get("model") or "Chaussure",
            suggested_area="Sport",
        )

    @property
    def is_on(self) -> bool:
        return self._get_item().get("replacement_needed", False)

    @property
    def extra_state_attributes(self):
        item = self._get_item()
        return {
            "gear_id": item.get("id"),
            "id": item.get("id"),
            "name": item.get("name"),
            "nom": item.get("name"),
            "brand": item.get("brand"),
            "marque": item.get("brand"),
            "model": item.get("model"),
            "modele": item.get("model"),
            "nickname": item.get("nickname"),
            "surnom": item.get("nickname"),
            "distance_km": item.get("distance_km"),
            "km_parcourus": item.get("distance_km"),
            "max_km": item.get("max_km"),
            "km_total": item.get("max_km"),
            "wear_pct": item.get("wear_pct"),
            "pourcentage_usure": item.get("wear_pct"),
            "remaining_km": item.get("remaining_km"),
            "km_restants": item.get("remaining_km"),
        }
