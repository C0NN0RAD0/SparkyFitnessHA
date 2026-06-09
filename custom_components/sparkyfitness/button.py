"""Button platform for SparkyFitness."""

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from . import SparkyFitnessConfigEntry
from .const import ATTRIBUTION, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: SparkyFitnessConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SparkyFitness button platform."""
    coordinator = entry.runtime_data.coordinator
    client = entry.runtime_data.client
    async_add_entities([LogWaterButton(coordinator, client, entry), LogMoodButton(coordinator, client, entry)])


class LogWaterButton(CoordinatorEntity, ButtonEntity):
    """Button to log 1 drink of the selected water container."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_icon = "mdi:water-plus"
    _attr_name = "Log Selected Water Container"

    def __init__(
        self, coordinator, client, entry: SparkyFitnessConfigEntry
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_log_water_btn"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Sparky Fitness",
            "model": "API Integration",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        containers = self.coordinator.data.get("water_containers", [])
        selected_container = None
        
        # 1. Look for the container currently selected in the UI dropdown
        selected_id = self._entry.runtime_data.selected_container_id
        if selected_id:
            for c in containers:
                if c.get("id") == selected_id:
                    selected_container = c
                    break
        
        # 2. Fallback to primary
        if not selected_container:
            for c in containers:
                if c.get("is_primary"):
                    selected_container = c
                    break
        
        # 3. Fallback to first
        if not selected_container and containers:
            selected_container = containers[0]

        if not selected_container:
            raise HomeAssistantError("No water container defined in Sparky Fitness")

        today = dt_util.now().date().isoformat()
        payload = {
            "entry_date": today,
            "change_drinks": 1.0,
            "container_id": selected_container["id"],
        }

        try:
            await self._client.async_post("/measurements/water-intake", json=payload)
            await self.coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to log water intake: {err}") from err

class LogMoodButton(CoordinatorEntity, ButtonEntity):
    """Button to log the selected mood."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_icon = "mdi:emoticon-plus"
    _attr_name = "Log Selected Mood"

    def __init__(
        self, coordinator, client, entry: SparkyFitnessConfigEntry
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_log_mood_btn"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Sparky Fitness",
            "model": "API Integration",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        selected_mood = self._entry.runtime_data.selected_mood
        if not selected_mood:
            selected_mood = 4 # Default to Good if none selected

        today = dt_util.now().date().isoformat()
        payload = {
            "entry_date": today,
            "mood_value": selected_mood,
        }

        try:
            await self._client.async_post("/mood", json=payload)
            await self.coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to log mood: {err}") from err
