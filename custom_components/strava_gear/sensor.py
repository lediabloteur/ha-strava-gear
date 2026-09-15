"""Sensor platform for Strava Gear."""
from homeassistant.components.sensor import SensorEntity
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
        entities.append(StravaShoeSensor(coordinator, entry, shoe["id"], shoe["name"]))

    for bike in coordinator.data.get("bikes", []):
        entities.append(StravaBikeSensor(coordinator, entry, bike["id"], bike["name"]))

    async_add_entities(entities)

class StravaGearBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor representing a piece of Strava equipment."""

    def __init__(self, coordinator, entry, gear_id, name, gear_type_label, icon):
        super().__init__(coordinator)
        self._gear_id = gear_id
        self._gear_name = name
        self._gear_type_label = gear_type_label
        self._attr_name = f"{gear_type_label} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{gear_id}"
        self._attr_native_unit_of_measurement = "km"
        self._attr_icon = icon

    def _get_item(self):
        for item in self.coordinator.data.get("shoes", []) + self.coordinator.data.get("bikes", []):
            if item["id"] == self._gear_id:
                return item
        return {}

    @property
    def device_info(self) -> DeviceInfo:
        item = self._get_item()
        return DeviceInfo(
            identifiers={(DOMAIN, self._gear_id)},
            name=f"{self._gear_type_label} {self._gear_name}",
            manufacturer=item.get("brand") or "Strava",
            model=item.get("model") or self._gear_type_label,
            suggested_area="Sport",
        )

    @property
    def native_value(self):
        return self._get_item().get("distance_km", 0.0)

    @property
    def extra_state_attributes(self):
        item = self._get_item()
        is_shoe = item.get("gear_type") == "shoe"
        attrs = {
            # Identifiants & classification
            "gear_id": item.get("id"),
            "id": item.get("id"),
            "id_strava": item.get("id"),
            "gear_type": item.get("gear_type"),
            "type_materiel": "chaussure" if is_shoe else "velo",
            "name": item.get("name"),
            "nom": item.get("name"),

            # Marque, modèle & surnom
            "brand": item.get("brand"),
            "brand_name": item.get("brand"),
            "marque": item.get("brand"),
            "model": item.get("model"),
            "model_name": item.get("model"),
            "modele": item.get("model"),
            "nickname": item.get("nickname"),
            "surnom": item.get("nickname"),
            "description": item.get("description"),

            # Kilométrages & distances
            "distance_km": item.get("distance_km"),
            "km_parcourus": item.get("distance_km"),
            "distance_meters": item.get("distance_meters"),
            "distance_metres": item.get("distance_meters"),
            "converted_distance": item.get("converted_distance"),
            "max_km": item.get("max_km"),
            "km_total": item.get("max_km"),
            "limite_km": item.get("max_km"),
            "notification_distance": item.get("notification_distance"),
            "remaining_km": item.get("remaining_km"),
            "km_restants": item.get("remaining_km"),
            "wear_pct": item.get("wear_pct"),
            "pourcentage_usure": item.get("wear_pct"),

            # Statuts
            "primary": item.get("primary", False),
            "principal": item.get("primary", False),
            "retired": item.get("retired", False),
            "retire": item.get("retired", False),
            "replacement_needed": item.get("replacement_needed", False),
            "remplacement_requis": item.get("replacement_needed", False),

            # Métadonnées Strava
            "resource_state": item.get("resource_state"),
        }

        # Données spécifiques éventuelles
        if item.get("frame_type") is not None:
            attrs["frame_type"] = item.get("frame_type")
            attrs["type_cadre"] = item.get("frame_type")
        if item.get("weight") is not None:
            attrs["weight"] = item.get("weight")
            attrs["poids"] = item.get("weight")

        # Objet brut Strava complet
        if item.get("strava_data"):
            attrs["strava_data"] = item.get("strava_data")

        return attrs

class StravaShoeSensor(StravaGearBaseSensor):
    def __init__(self, coordinator, entry, gear_id, name):
        super().__init__(coordinator, entry, gear_id, name, "Chaussure", "mdi:shoe-sneaker")

class StravaBikeSensor(StravaGearBaseSensor):
    def __init__(self, coordinator, entry, gear_id, name):
        super().__init__(coordinator, entry, gear_id, name, "Vélo", "mdi:bicycle")
