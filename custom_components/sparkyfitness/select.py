"""Select platform for SparkyFitness."""

from typing import Any
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import CONF_NAME
from . import SparkyFitnessConfigEntry
from .const import ATTRIBUTION, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: SparkyFitnessConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SparkyFitness select platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([WaterContainerSelect(coordinator, entry), MoodSelect(coordinator, entry)])


class WaterContainerSelect(CoordinatorEntity, RestoreEntity, SelectEntity):
    """Select entity to choose the active water container."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_icon = "mdi:cup-water"
    _attr_name = "Water Container"

    def __init__(self, coordinator, entry: SparkyFitnessConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_water_container"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data.get(CONF_NAME, "Sparky Fitness"),
            "manufacturer": "Sparky Fitness",
        }
        self._container_map: dict[str, str] = {}
        self._attr_current_option = None

    @property
    def options(self) -> list[str]:
        """Return the available water containers."""
        containers = self.coordinator.data.get("water_containers", [])
        self._container_map = {c.get("name"): c.get("id") for c in containers if c.get("name") and c.get("id")}
        return list(self._container_map.keys())

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            self._attr_current_option = last_state.state
        
        self._update_runtime_data()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_runtime_data()
        super()._handle_coordinator_update()

    def _update_runtime_data(self) -> None:
        """Update runtime data and fallback options."""
        containers = self.coordinator.data.get("water_containers", [])
        self._container_map = {c.get("name"): c.get("id") for c in containers if c.get("name") and c.get("id")}
        
        # If no option selected, or selected option is invalid, fallback
        if not self._attr_current_option or self._attr_current_option not in self._container_map:
            self._attr_current_option = None
            for c in containers:
                if c.get("is_primary"):
                    self._attr_current_option = c.get("name")
                    break
            
            if not self._attr_current_option and containers and containers[0].get("name"):
                self._attr_current_option = containers[0].get("name")

        if self._attr_current_option and self._attr_current_option in self._container_map:
            self._entry.runtime_data.selected_container_id = self._container_map[self._attr_current_option]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in self._container_map:
            self._attr_current_option = option
            self._entry.runtime_data.selected_container_id = self._container_map[option]
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Unknown water container selected: %s", option)

class MoodSelect(CoordinatorEntity, RestoreEntity, SelectEntity):
    """Select entity to choose the mood to log."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_icon = "mdi:emoticon"
    _attr_name = "Mood Selection"

    def __init__(self, coordinator, entry: SparkyFitnessConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_mood_selection"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data.get(CONF_NAME, "Sparky Fitness"),
            "manufacturer": "Sparky Fitness",
        }
        self._mood_map: dict[str, int] = {
            "Amazing": 5,
            "Good": 4,
            "Okay": 3,
            "Bad": 2,
            "Terrible": 1,
        }
        self._attr_options = list(self._mood_map.keys())
        self._attr_current_option = "Good" # Default
        self._entry.runtime_data.selected_mood = 4

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            if last_state.state in self._mood_map:
                self._attr_current_option = last_state.state
                self._entry.runtime_data.selected_mood = self._mood_map[last_state.state]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in self._mood_map:
            self._attr_current_option = option
            self._entry.runtime_data.selected_mood = self._mood_map[option]
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Unknown mood selected: %s", option)
