"""Sensor platform for SparkyFitness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfMass, UnitOfTime, UnitOfVolume
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


GOAL_SENSORS: tuple[SparkyFitnessSensorDescription, ...] = (
    SparkyFitnessSensorDescription(
        key="calories",
        name="Daily Calorie Goal",
        icon="mdi:target",
        unit="kcal",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="protein",
        name="Daily Protein Goal",
        icon="mdi:target",
        unit="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="carbs",
        name="Daily Carbs Goal",
        icon="mdi:target",
        unit="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="fat",
        name="Daily Fat Goal",
        icon="mdi:target",
        unit="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="water_goal_ml",
        name="Daily Water Goal",
        icon="mdi:target",
        unit="ml",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


FASTING_STATS_SENSORS: tuple[SparkyFitnessSensorDescription, ...] = (
    SparkyFitnessSensorDescription(
        key="total_completed_fasts",
        name="Total Completed Fasts",
        icon="mdi:calendar-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SparkyFitnessSensorDescription(
        key="average_duration_minutes",
        name="Average Fast Duration",
        icon="mdi:timer-sand",
        unit="h",
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

    entities: list[SensorEntity] = [
        CheckInSensor(coordinator, description) for description in CHECK_IN_SENSORS
    ]
    
    entities.extend([
        DailySummarySensor(coordinator, description) for description in DAILY_SENSORS
    ])

    entities.extend([
        GoalSensor(coordinator, description) for description in GOAL_SENSORS
    ])

    entities.extend([
        FastingStatsSensor(coordinator, description) for description in FASTING_STATS_SENSORS
    ])
    
    entities.extend([
        SleepDurationSensor(coordinator),
        ExerciseDurationSensor(coordinator),
        ExerciseCaloriesSensor(coordinator),
        WaterIntakeSensor(coordinator),
        MoodSensor(coordinator),
        FastingStatusSensor(coordinator),
    ])

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
    def native_value(self) -> float | int | None:
        """Return state from the current check-in payload."""
        payload = self.coordinator.data.get("check_in", {})
        value = payload.get(self._key)
        val = _as_float(value)
        if val is None:
            return None
        if self._key == "steps":
            return int(val)
        return round(val, 1)


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
    def native_value(self) -> float | int | None:
        """Return state from daily summary payload."""
        payload = self.coordinator.data.get("daily_summary", {})
        value = payload.get(f"total_{self._key}") or payload.get(self._key)
        val = _as_float(value)
        if val is None:
            return None
        if self._key == "calories":
            return int(round(val))
        return round(val, 1)


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
        if minutes is not None:
            value = _as_float(minutes)
        else:
            seconds = payload.get("duration_seconds")
            value = _as_float(seconds) / 60.0 if seconds is not None else None

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
        return round(total, 1)


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
    def native_value(self) -> int | None:
        """Return total exercise calories from current payload."""
        exercises = self.coordinator.data.get("exercises", [])
        total = 0.0
        for item in exercises:
            if isinstance(item, dict):
                total += _as_float(item.get("calories_burned")) or 0.0
        return int(round(total))


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
    def native_value(self) -> int | None:
        """Return water intake in ml."""
        payload = self.coordinator.data.get("water", {})
        value = payload.get("water_ml")
        if value is not None:
            val = _as_float(value)
            return int(round(val)) if val is not None else 0
        return 0


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
        label = payload.get("mood_label")
        if label is not None:
            return str(label)
        
        value = payload.get("mood_value")
        if value is None:
            return None
            
        mapping = {
            1: "Awful",
            2: "Bad",
            3: "Okay",
            4: "Good",
            5: "Excellent",
        }
        return mapping.get(int(value), str(value))


def _as_float(value: Any) -> float | None:
    """Convert a value to float safely."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class GoalSensor(SparkyFitnessCoordinatorSensor):
    """Daily target goal sensor."""

    def __init__(self, coordinator, description: SparkyFitnessSensorDescription) -> None:
        super().__init__(
            coordinator,
            unique_key=f"goal_{description.key}",
            name=description.name,
            icon=description.icon,
        )
        self._key = description.key
        self._attr_native_unit_of_measurement = description.unit
        self._attr_state_class = description.state_class

    @property
    def native_value(self) -> float | int | None:
        """Return target value from goals payload."""
        payload = self.coordinator.data.get("goals", {})
        value = payload.get(self._key)
        val = _as_float(value)
        if val is None:
            return None
        if self._key in ("calories", "water_goal_ml"):
            return int(round(val))
        return round(val, 1)


class FastingStatsSensor(SparkyFitnessCoordinatorSensor):
    """Fasting statistics sensor."""

    def __init__(self, coordinator, description: SparkyFitnessSensorDescription) -> None:
        super().__init__(
            coordinator,
            unique_key=f"fasting_stats_{description.key}",
            name=description.name,
            icon=description.icon,
        )
        self._key = description.key
        self._attr_native_unit_of_measurement = description.unit
        self._attr_state_class = description.state_class

    @property
    def native_value(self) -> float | int | None:
        """Return fasting stats from payload."""
        payload = self.coordinator.data.get("fasting_stats", {})
        value = payload.get(self._key)
        if value is None:
            return None
            
        val = _as_float(value)
        if val is None:
            return None
            
        if self._key == "average_duration_minutes":
            return round(val / 60.0, 2)
            
        return int(round(val))


class FastingStatusSensor(SparkyFitnessCoordinatorSensor):
    """Current fasting status sensor."""

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="fasting_status",
            name="Fasting Status",
            icon="mdi:clock-fast",
        )

    @property
    def native_value(self) -> str | None:
        """Return Fasting or Not Fasting status."""
        active_fast = self.coordinator.data.get("fasting_current")
        if active_fast and active_fast.get("id"):
            return "Fasting"
        return "Not Fasting"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes of the fast."""
        active_fast = self.coordinator.data.get("fasting_current")
        if not active_fast or not active_fast.get("id"):
            return None

        start_time_str = active_fast.get("start_time")
        target_end_str = active_fast.get("target_end_time")
        fasting_type = active_fast.get("fasting_type", "Intermittent Fasting")

        duration_hours = None
        if start_time_str:
            try:
                start_dt = dt_util.parse_datetime(start_time_str)
                if start_dt:
                    now = dt_util.utcnow()
                    delta = now - start_dt
                    duration_hours = round(delta.total_seconds() / 3600.0, 2)
            except Exception:
                pass

        return {
            "fast_id": active_fast.get("id"),
            "start_time": start_time_str,
            "target_end_time": target_end_str,
            "fasting_type": fasting_type,
            "duration_hours": duration_hours,
        }
