"""Sensor platform for SparkyFitness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime, UnitOfVolume
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


DAILY_SENSORS: tuple[SparkyFitnessSensorDescription, ...] = (
    SparkyFitnessSensorDescription(
        key="calories",
        name="Daily Calories",
        icon="mdi:fire",
        unit="kcal",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="protein",
        name="Daily Protein",
        icon="mdi:dna",
        unit="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="carbs",
        name="Daily Carbs",
        icon="mdi:bread-slice",
        unit="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="fat",
        name="Daily Fat",
        icon="mdi:water-outline",
        unit="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SparkyFitness sensors from a config entry."""
    config_entry = entry
    runtime = config_entry.runtime_data
    coordinator = runtime.coordinator

    entities: list[SensorEntity] = [
        DailySummarySensor(coordinator, description) for description in DAILY_SENSORS
    ]
    entities.extend(
        [
            MeasurementSensor(coordinator, "weight", "Body Weight", UnitOfMass.KILOGRAMS),
            MeasurementSensor(
                coordinator,
                "body_fat_percentage",
                "Body Fat Percentage",
                "%",
            ),
            SleepDurationSensor(coordinator),
            ExerciseDurationSensor(coordinator),
            ExerciseCaloriesSensor(coordinator),
            WaterIntakeSensor(coordinator),
            MoodSensor(coordinator),
        ]
    )

    async_add_entities(entities)


class SparkyFitnessCoordinatorSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for SparkyFitness entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator, unique_key: str, name: str, icon: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{unique_key}"
        self._attr_name = name
        self._attr_icon = icon


class DailySummarySensor(SparkyFitnessCoordinatorSensor):
    """Daily macro summary sensor."""

    def __init__(self, coordinator, description: SparkyFitnessSensorDescription) -> None:
        super().__init__(
            coordinator,
            unique_key=f"daily_{description.key}",
            name=description.name,
            icon=description.icon,
        )
        self._key = description.key
        self._attr_native_unit_of_measurement = description.unit
        self._attr_state_class = description.state_class

    @property
    def native_value(self) -> float | None:
        """Return state from daily summary payload."""
        payload = self.coordinator.data.get("daily_summary", {})
        value = payload.get(self._key)
        return _as_float(value)


class MeasurementSensor(SparkyFitnessCoordinatorSensor):
    """Measurement sensor from the latest measurement object."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, key: str, name: str, unit: str) -> None:
        super().__init__(
            coordinator,
            unique_key=f"measurement_{key}",
            name=name,
            icon="mdi:scale-bathroom",
        )
        self._key = key
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        """Return measurement value from latest entry."""
        measurements = self.coordinator.data.get("measurements", [])
        if not measurements:
            return None

        latest = measurements[0]
        if not isinstance(latest, dict):
            return None

        return _as_float(latest.get(self._key))


class SleepDurationSensor(SparkyFitnessCoordinatorSensor):
    """Sleep duration sensor in hours."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.HOURS

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="sleep_duration",
            name="Sleep Duration",
            icon="mdi:bed",
        )

    @property
    def native_value(self) -> float | None:
        """Return sleep duration in hours."""
        payload = self.coordinator.data.get("sleep", {})
        minutes = payload.get("duration_minutes")
        value = _as_float(minutes)
        if value is None:
            return None
        return round(value / 60.0, 2)


class ExerciseDurationSensor(SparkyFitnessCoordinatorSensor):
    """Total exercise duration in minutes."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="exercise_duration",
            name="Exercise Duration",
            icon="mdi:dumbbell",
        )

    @property
    def native_value(self) -> float | None:
        """Return total exercise duration from current payload."""
        exercises = self.coordinator.data.get("exercises", [])
        total = 0.0
        for item in exercises:
            if isinstance(item, dict):
                total += _as_float(item.get("duration_minutes")) or 0.0
        return total if total > 0 else None


class ExerciseCaloriesSensor(SparkyFitnessCoordinatorSensor):
    """Total exercise calories burned."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "kcal"

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="exercise_calories",
            name="Exercise Calories",
            icon="mdi:fire",
        )

    @property
    def native_value(self) -> float | None:
        """Return total exercise calories from current payload."""
        exercises = self.coordinator.data.get("exercises", [])
        total = 0.0
        for item in exercises:
            if isinstance(item, dict):
                total += _as_float(item.get("calories_burned")) or 0.0
        return total if total > 0 else None


class WaterIntakeSensor(SparkyFitnessCoordinatorSensor):
    """Water intake sensor in milliliters."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfVolume.MILLILITERS

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="water_intake",
            name="Water Intake",
            icon="mdi:water",
        )

    @property
    def native_value(self) -> float | None:
        """Return water intake in ml."""
        payload = self.coordinator.data.get("daily_summary", {})
        return _as_float(payload.get("water_intake_ml"))


class MoodSensor(SparkyFitnessCoordinatorSensor):
    """Current mood sensor."""

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="current_mood",
            name="Current Mood",
            icon="mdi:emoticon",
        )

    @property
    def native_value(self) -> str | None:
        """Return latest mood label."""
        payload = self.coordinator.data.get("mood", {})
        value = payload.get("mood_label")
        if value is None:
            return None
        return str(value)


def _as_float(value: Any) -> float | None:
    """Convert value to float safely."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
