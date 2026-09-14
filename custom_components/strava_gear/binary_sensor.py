"""Binary sensor platform for Strava Gear wear alerts."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    def is_on(self) -> bool:
        return self._get_item().get("replacement_needed", False)
