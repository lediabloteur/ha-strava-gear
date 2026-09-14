"""Sensor platform for Strava Gear."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for shoe in coordinator.data.get("shoes", []):
        entities.append(StravaShoeSensor(coordinator, entry, shoe["id"], shoe["name"]))

    for bike in coordinator.data.get("bikes", []):
        entities.append(StravaBikeSensor(coordinator, entry, bike["id"], bike["name"]))

    async_add_entities(entities)

class StravaShoeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, gear_id, name):
        super().__init__(coordinator)
        self._gear_id = gear_id
        self._attr_name = f"Chaussure {name}"
        self._attr_unique_id = f"{entry.entry_id}_{gear_id}"
        self._attr_native_unit_of_measurement = "km"
        self._attr_icon = "mdi:shoe-sneaker"

    def _get_item(self):
        for s in self.coordinator.data.get("shoes", []):
            if s["id"] == self._gear_id:
                return s
        return {}

    @property
    def native_value(self):
        return self._get_item().get("distance_km", 0.0)

    @property
    def extra_state_attributes(self):
        item = self._get_item()
        return {
            "brand": item.get("brand"),
            "model": item.get("model"),
            "notification_distance": item.get("notification_distance"),
            "max_km": item.get("max_km"),
            "remaining_km": item.get("remaining_km"),
            "wear_pct": item.get("wear_pct"),
            "primary": item.get("primary"),
            "retired": item.get("retired", False),
        }

class StravaBikeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, gear_id, name):
        super().__init__(coordinator)
        self._gear_id = gear_id
        self._attr_name = f"Vélo {name}"
        self._attr_unique_id = f"{entry.entry_id}_{gear_id}"
        self._attr_native_unit_of_measurement = "km"
        self._attr_icon = "mdi:bicycle"

    def _get_item(self):
        for b in self.coordinator.data.get("bikes", []):
            if b["id"] == self._gear_id:
                return b
        return {}

    @property
    def native_value(self):
        return self._get_item().get("distance_km", 0.0)

    @property
    def extra_state_attributes(self):
        item = self._get_item()
        attrs = {
            "brand": item.get("brand"),
            "model": item.get("model"),
            "primary": item.get("primary"),
            "retired": item.get("retired", False),
        }
        if item.get("max_km") is not None:
            attrs["notification_distance"] = item.get("notification_distance")
            attrs["max_km"] = item.get("max_km")
            attrs["remaining_km"] = item.get("remaining_km")
            attrs["wear_pct"] = item.get("wear_pct")
        return attrs
