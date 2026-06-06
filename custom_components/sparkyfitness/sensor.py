"""Sensor platform for SparkyFitness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SparkyFitnessConfigEntry
from .const import ATTRIBUTION, DOMAIN


@dataclass(frozen=True)
class SparkyFitnessSensorDescription:
    """Describe a SparkyFitness sensor."""

    key: str
    name: str
    icon: str
    unit: str | None = None
    state_class: SensorStateClass | None = None


CHECK_IN_SENSORS: tuple[SparkyFitnessSensorDescription, ...] = (
    SparkyFitnessSensorDescription(
        key="weight",
        name="Body Weight",
        icon="mdi:scale-bathroom",
        unit=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="body_fat",
        name="Body Fat",
        icon="mdi:percent",
        unit="%",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="bmi",
        name="BMI",
        icon="mdi:chart-box-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="steps",
        name="Steps",
        icon="mdi:walk",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="neck",
        name="Neck",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="chest",
        name="Chest",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="waist",
        name="Waist",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="hips",
        name="Hips",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="thigh",
        name="Thigh",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="calf",
        name="Calf",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="bicep",
        name="Bicep",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="forearm",
        name="Forearm",
        icon="mdi:ruler",
        unit=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SparkyFitness sensors from a config entry."""
    runtime = entry.runtime_data
    coordinator = runtime.coordinator

    async_add_entities(
        [CheckInSensor(coordinator, description) for description in CHECK_IN_SENSORS]
    )


class SparkyFitnessCoordinatorSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for SparkyFitness entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator, unique_key: str, name: str, icon: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{unique_key}"
        self._attr_name = name
        self._attr_icon = icon


class CheckInSensor(SparkyFitnessCoordinatorSensor):
    """Sensor for daily check-in measurement fields."""

    def __init__(self, coordinator, description: SparkyFitnessSensorDescription) -> None:
        super().__init__(
            coordinator,
            unique_key=f"check_in_{description.key}",
            name=description.name,
            icon=description.icon,
        )
        self._key = description.key
        self._attr_native_unit_of_measurement = description.unit
        self._attr_state_class = description.state_class

    @property
    def native_value(self) -> float | None:
        """Return state from the current check-in payload."""
        payload = self.coordinator.data.get("check_in", {})
        value = payload.get(self._key)
        return _as_float(value)


def _as_float(value: Any) -> float | None:
    """Convert a value to float safely."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
