"""Sensor platform for SparkyFitness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass, RestoreSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, UnitOfLength, UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        key="body_fat_percentage",
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
    SparkyFitnessSensorDescription(
        key="dietary_fiber",
        name="Daily Fiber",
        icon="mdi:leaf",
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
        SleepScoreSensor(coordinator),
        DeepSleepSensor(coordinator),
        RemSleepSensor(coordinator),
        LightSleepSensor(coordinator),
        ExerciseDurationSensor(coordinator),
        ExerciseCaloriesSensor(coordinator),
        CaloriesRemainingSensor(coordinator),
        WaterIntakeSensor(coordinator),
        MoodSensor(coordinator),
        FastingStatusSensor(coordinator),
    ])

    custom_categories = coordinator.data.get("custom_categories", [])
    entities.extend([
        CustomMeasurementSensor(coordinator, category)
        for category in custom_categories
        if isinstance(category, dict) and category.get("id")
    ])

    entities.extend([
        SparkyFitnessHealthSensor(coordinator, entry),
        SparkyFitnessLatencySensor(coordinator),
    ])

    async_add_entities(entities)


class SparkyFitnessCoordinatorSensor(CoordinatorEntity, RestoreSensor):
    """Base sensor for SparkyFitness entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator, unique_key: str, name: str, icon: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{unique_key}"
        self._attr_name = name
        self._attr_icon = icon
        self._restored_native_value = None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
            self._restored_native_value = last_sensor_data.native_value

    @property
    def native_value(self):
        """Return the state of the sensor."""
        val = self._get_native_value()
        if val is None and self._restored_native_value is not None:
            return self._restored_native_value
        return val

    def _get_native_value(self):
        """Override this method in subclasses to return the actual state."""
        return None


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

    def _get_native_value(self) -> float | int | None:
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

    def _get_native_value(self) -> float | int | None:
        """Return state from daily summary payload."""
        payload = self.coordinator.data.get("daily_summary", {})
        value = payload.get(f"total_{self._key}")
        if value is None:
            value = payload.get(self._key)
        val = _as_float(value)
        if val is None:
            return None
        if self._key == "calories":
            return int(round(val))
        return round(val, 1)


class SleepDurationSensor(SparkyFitnessCoordinatorSensor):
    """Total sleep window in hours (bedtime to wake time)."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.HOURS

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="sleep_duration",
            name="Sleep Duration",
            icon="mdi:bed",
        )

    def _get_native_value(self) -> float | None:
        """Return total sleep window in hours from duration_in_seconds."""
        payload = self.coordinator.data.get("sleep", {})
        if not payload:
            return None
        # Confirmed live API field: duration_in_seconds (total window bedtime→wake)
        val = _as_float(payload.get("duration_in_seconds"))
        if val is not None:
            return round(val / 3600.0, 2)
        # Fallback: compute from bedtime/wake_time
        bedtime = payload.get("bedtime")
        wake = payload.get("wake_time")
        if bedtime and wake:
            try:
                from homeassistant.util import dt as dt_util
                b = dt_util.parse_datetime(str(bedtime))
                w = dt_util.parse_datetime(str(wake))
                if b and w and w > b:
                    return round((w - b).total_seconds() / 3600.0, 2)
            except Exception:
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose rich sleep fields as attributes."""
        payload = self.coordinator.data.get("sleep", {})
        if not payload:
            return None
        asleep_s = _as_float(payload.get("time_asleep_in_seconds"))
        return {
            "bedtime": payload.get("bedtime"),
            "wake_time": payload.get("wake_time"),
            "time_asleep_hours": round(asleep_s / 3600.0, 2) if asleep_s is not None else None,
            "sleep_score": payload.get("sleep_score"),
            "source": payload.get("source"),
            "deep_sleep_minutes": round(_as_float(payload.get("deep_sleep_seconds") or 0) / 60, 1),
            "rem_sleep_minutes": round(_as_float(payload.get("rem_sleep_seconds") or 0) / 60, 1),
            "light_sleep_minutes": round(_as_float(payload.get("light_sleep_seconds") or 0) / 60, 1),
            "awake_minutes": round(_as_float(payload.get("awake_sleep_seconds") or 0) / 60, 1),
        }


class SleepScoreSensor(SparkyFitnessCoordinatorSensor):
    """Sleep quality score (0–100)."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:sleep"

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="sleep_score",
            name="Sleep Score",
            icon="mdi:sleep",
        )

    def _get_native_value(self) -> int | None:
        payload = self.coordinator.data.get("sleep", {})
        val = _as_float(payload.get("sleep_score"))
        return int(val) if val is not None else None


class DeepSleepSensor(SparkyFitnessCoordinatorSensor):
    """Deep sleep duration in minutes."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="deep_sleep",
            name="Deep Sleep",
            icon="mdi:bed-clock",
        )

    def _get_native_value(self) -> float | None:
        payload = self.coordinator.data.get("sleep", {})
        val = _as_float(payload.get("deep_sleep_seconds"))
        return round(val / 60.0, 1) if val is not None else None


class RemSleepSensor(SparkyFitnessCoordinatorSensor):
    """REM sleep duration in minutes."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="rem_sleep",
            name="REM Sleep",
            icon="mdi:head-dots-horizontal",
        )

    def _get_native_value(self) -> float | None:
        payload = self.coordinator.data.get("sleep", {})
        val = _as_float(payload.get("rem_sleep_seconds"))
        return round(val / 60.0, 1) if val is not None else None


class LightSleepSensor(SparkyFitnessCoordinatorSensor):
    """Light sleep duration in minutes."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="light_sleep",
            name="Light Sleep",
            icon="mdi:weather-night-partly-cloudy",
        )

    def _get_native_value(self) -> float | None:
        payload = self.coordinator.data.get("sleep", {})
        val = _as_float(payload.get("light_sleep_seconds"))
        return round(val / 60.0, 1) if val is not None else None


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

    def _get_native_value(self) -> float | None:
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
    def _get_native_value(self) -> int | None:
        """Return total exercise calories from current payload."""
        exercises = self.coordinator.data.get("exercises", [])
        total = 0.0
        for item in exercises:
            if isinstance(item, dict):
                total += _as_float(item.get("calories_burned")) or 0.0
        return int(round(total))


class CaloriesRemainingSensor(SparkyFitnessCoordinatorSensor):
    """Remaining calories for the day."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "kcal"

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="calories_remaining",
            name="Calories Remaining",
            icon="mdi:calculator",
        )

    def _get_native_value(self) -> float | None:
        """Calculate calories remaining: Goal - Consumed."""
        goals = self.coordinator.data.get("goals", {})
        summary = self.coordinator.data.get("daily_summary", {})

        goal_cals = _as_float(goals.get("calories"))
        consumed_cals = _as_float(summary.get("total_calories"))

        if goal_cals is not None and consumed_cals is not None:
            return round(goal_cals - consumed_cals, 2)
        return None


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

    def _get_native_value(self) -> int | None:
        """Return water intake in ml."""
        payload = self.coordinator.data.get("water", {})
        value = payload.get("water_ml")
        if value is not None:
            val = _as_float(value)
            return int(round(val)) if val is not None else 0
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes of the water sensor."""
        containers = self.coordinator.data.get("water_containers", [])
        return {
            "containers": [
                {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "volume": c.get("volume"),
                    "unit": c.get("unit"),
                    "is_primary": c.get("is_primary"),
                }
                for c in containers
            ]
        }


class MoodSensor(SparkyFitnessCoordinatorSensor):
    """Current mood sensor."""

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="current_mood",
            name="Current Mood",
            icon="mdi:emoticon",
        )

    def _get_native_value(self) -> str | None:
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

    def _get_native_value(self) -> float | int | None:
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

    def _get_native_value(self) -> float | int | None:
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

    def _get_native_value(self) -> str | None:
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


class CustomMeasurementSensor(SparkyFitnessCoordinatorSensor):
    """Sensor for custom fitness and health measurements."""

    def __init__(self, coordinator, category: dict[str, Any]) -> None:
        name = category.get("name", "Custom Measurement")
        display_name = category.get("display_name") or name.replace("_", " ").title()
        unit = category.get("measurement_type")
        
        super().__init__(
            coordinator,
            unique_key=f"custom_{category['id']}",
            name=display_name,
            icon="mdi:chart-bell-curve-cumulative",
        )
        self._category = category
        self._category_id = category["id"]
        self._attr_native_unit_of_measurement = unit
        if category.get("data_type") == "numeric":
            self._attr_state_class = SensorStateClass.MEASUREMENT

    def _get_native_value(self) -> float | str | bool | None:
        """Return value of the custom measurement for today."""
        entries = self.coordinator.data.get("custom_entries", [])
        for entry in entries:
            if isinstance(entry, dict) and entry.get("category_id") == self._category_id:
                val = entry.get("value")
                if val is None:
                    return None
                data_type = self._category.get("data_type")
                if data_type == "numeric":
                    return _as_float(val)
                elif data_type == "boolean":
                    return str(val).lower() in ("true", "1", "yes")
                return str(val)
        return None


class SparkyFitnessHealthSensor(SparkyFitnessCoordinatorSensor):
    """Sensor reporting the health/reachability of the Sparky Fitness instance."""

    _attr_entity_category = None
    _attr_icon = "mdi:heart-pulse"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            unique_key="instance_health",
            name="Instance Health",
            icon="mdi:heart-pulse",
        )
        self._entry = entry

    @property
    def available(self) -> bool:
        """Always available so we can display Offline instead of unavailable."""
        return True

    def _get_native_value(self) -> str:
        """Return Online when coordinator is healthy, Offline otherwise."""
        if not self.coordinator.last_update_success:
            return "Offline"
        stats = self.coordinator.data.get("health_stats", {})
        return stats.get("status", "Online")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return health statistics as state attributes."""
        stats = self.coordinator.data.get("health_stats", {}) if self.coordinator.data else {}
        server_url = (
            f"{self._entry.data.get(_CONF_SCHEME_CONST, 'https')}://"
            f"{self._entry.data.get(CONF_HOST, 'unknown')}"
        )
        return {
            "server_url": server_url,
            "latency_seconds": stats.get("latency_seconds"),
            "last_successful_update": stats.get("last_successful_update"),
            "custom_categories_count": stats.get("custom_categories_count", 0),
        }


class SparkyFitnessLatencySensor(SparkyFitnessCoordinatorSensor):
    """Sensor reporting the total API poll round-trip latency in seconds."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            unique_key="api_latency",
            name="API Latency",
            icon="mdi:timer-outline",
        )

    def _get_native_value(self) -> float | None:
        """Return last measured API round-trip latency in seconds."""
        if not self.coordinator.last_update_success or not self.coordinator.data:
            return None
        stats = self.coordinator.data.get("health_stats", {})
        return stats.get("latency_seconds")
