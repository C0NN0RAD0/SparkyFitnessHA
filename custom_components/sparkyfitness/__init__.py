"""The SparkyFitness integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any, TypeAlias

from aiohttp import ClientError, ClientResponseError, ClientSession
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    API_TIMEOUT_SECONDS,
    CONF_SCHEME,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class SparkyFitnessConfig:
    """Config data used by the API client."""

    base_url: str
    token: str


class SparkyFitnessApiClient:
    """Simple async API client for SparkyFitness endpoints."""

    def __init__(self, session: ClientSession, config: SparkyFitnessConfig) -> None:
        self._session = session
        self._base_url = config.base_url.rstrip("/")
        self._token = config.token

    async def async_get(self, endpoint: str) -> Any:
        """GET JSON from a SparkyFitness API endpoint."""
        url = f"{self._base_url}/api{endpoint}"
        headers = {"Authorization": f"Bearer {self._token}"}

        try:
            async with async_timeout.timeout(API_TIMEOUT_SECONDS):
                async with self._session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    payload = await response.json(content_type=None)
        except ClientResponseError:
            raise
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Request failed for endpoint {endpoint}: {err}") from err

        return payload

    async def async_post(self, endpoint: str, json: dict[str, Any] | None = None) -> Any:
        """POST JSON to a SparkyFitness API endpoint."""
        url = f"{self._base_url}/api{endpoint}"
        headers = {"Authorization": f"Bearer {self._token}"}

        try:
            async with async_timeout.timeout(API_TIMEOUT_SECONDS):
                async with self._session.post(url, headers=headers, json=json) as response:
                    response.raise_for_status()
                    payload = await response.json(content_type=None)
        except ClientResponseError:
            raise
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Request failed for endpoint {endpoint}: {err}") from err

        return payload



@dataclass
class SparkyFitnessRuntimeData:
    """Runtime data attached to each config entry."""

    client: SparkyFitnessApiClient
    coordinator: DataUpdateCoordinator[dict[str, Any]]


SparkyFitnessConfigEntry: TypeAlias = ConfigEntry[SparkyFitnessRuntimeData]


async def _async_update_data(client: SparkyFitnessApiClient) -> dict[str, Any]:
    """Fetch all datasets used by entities."""
    today = dt_util.now().date().isoformat()
    data: dict[str, Any] = {
        "check_in": {},
        "daily_summary": {},
        "sleep": {},
        "exercises": [],
        "water": {},
        "mood": {},
        "fasting_current": {},
        "fasting_stats": {},
        "goals": {},
        "water_containers": [],
        "custom_categories": [],
        "custom_entries": [],
    }

    endpoints = {
        "check_in": f"/measurements/check-in/{today}",
        "daily_summary": f"/food-entries/nutrition/today?date={today}",
        "sleep": f"/sleep?startDate={today}&endDate={today}",
        "exercises": f"/exercise-entries/by-date?selectedDate={today}",
        "water": f"/measurements/water-intake/{today}",
        "mood": f"/mood/date/{today}",
        "fasting_current": "/fasting/current",
        "fasting_stats": "/fasting/stats",
        "goals": f"/goals/by-date/{today}",
        "water_containers": "/water-containers",
        "custom_categories": "/measurements/custom-categories",
        "custom_entries": f"/measurements/custom-entries/{today}",
    }

    for key, endpoint in endpoints.items():
        try:
            response = await client.async_get(endpoint)
            if key in ("exercises", "water_containers", "custom_categories", "custom_entries"):
                data[key] = response if isinstance(response, list) else []
            elif key == "sleep":
                data[key] = response[0] if isinstance(response, list) and len(response) > 0 else {}
            elif key == "fasting_current":
                data[key] = response if isinstance(response, dict) else {}
            else:
                data[key] = response if response is not None else {}
        except ClientResponseError as err:
            if err.status == 401:
                raise UpdateFailed("Authentication failed") from err
            if err.status == 404:
                # 404 is a valid state if no logs/checkins exist for today yet
                _LOGGER.debug("Endpoint %s returned 404 (no data for today)", endpoint)
                continue
            raise UpdateFailed(f"API error for {endpoint}: HTTP {err.status}") from err
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Unexpected update error on {endpoint}: {err}") from err

    return data


START_FAST_SCHEMA = vol.Schema({
    vol.Required("fasting_type"): cv.string,
    vol.Optional("target_duration_hours"): vol.Coerce(int),
})

END_FAST_SCHEMA = vol.Schema({
    vol.Optional("mood_value"): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
    vol.Optional("notes"): cv.string,
})

LOG_WATER_SCHEMA = vol.Schema(
    vol.All(
        vol.Schema({
            vol.Optional("amount_ml"): vol.Coerce(int),
            vol.Optional("drinks"): vol.Coerce(float),
            vol.Optional("container"): cv.string,
        }),
        cv.has_at_least_one_key("amount_ml", "drinks"),
    )
)

LOG_MOOD_SCHEMA = vol.Schema({
    vol.Required("mood_value"): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
    vol.Optional("notes"): cv.string,
})

LOG_CHECK_IN_SCHEMA = vol.Schema({
    vol.Optional("weight"): vol.Coerce(float),
    vol.Optional("body_fat"): vol.Coerce(float),
})


async def async_setup_entry(hass: HomeAssistant, entry: SparkyFitnessConfigEntry) -> bool:
    """Set up SparkyFitness from a config entry."""
    session = async_get_clientsession(
        hass, verify_ssl=entry.data[CONF_VERIFY_SSL]
    )
    config = SparkyFitnessConfig(
        base_url=f"{entry.data.get(CONF_SCHEME, 'https')}://{entry.data[CONF_HOST]}",
        token=entry.data[CONF_TOKEN],
    )
    client = SparkyFitnessApiClient(session, config)

    coordinator: DataUpdateCoordinator[dict[str, Any]] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.data.get(CONF_NAME, 'default')}",
        update_method=lambda: _async_update_data(client),
        update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = SparkyFitnessRuntimeData(client=client, coordinator=coordinator)

    # Register services
    async def handle_start_fast(call):
        """Handle start fast service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Sparky Fitness integration not configured")
        entry = entries[0]
        client = entry.runtime_data.client
        coordinator = entry.runtime_data.coordinator

        fasting_type = call.data["fasting_type"]
        duration = call.data.get("target_duration_hours")

        start_time = dt_util.utcnow()
        payload = {
            "start_time": start_time.isoformat().replace("+00:00", "Z"),
            "fasting_type": fasting_type,
        }
        if duration:
            target_end = start_time + timedelta(hours=duration)
            payload["target_end_time"] = target_end.isoformat().replace("+00:00", "Z")

        try:
            await client.async_post("/fasting/start", json=payload)
            await coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to start fast: {err}") from err

    async def handle_end_fast(call):
        """Handle end fast service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Sparky Fitness integration not configured")
        entry = entries[0]
        client = entry.runtime_data.client
        coordinator = entry.runtime_data.coordinator

        active_fast = coordinator.data.get("fasting_current")
        if not active_fast or not active_fast.get("id"):
            raise HomeAssistantError("No active fast found to end")

        fast_id = active_fast["id"]
        end_time = dt_util.utcnow()

        payload = {
            "id": fast_id,
            "end_time": end_time.isoformat().replace("+00:00", "Z"),
        }

        mood_value = call.data.get("mood_value")
        notes = call.data.get("notes")
        if mood_value is not None:
            payload["mood"] = {
                "value": mood_value,
            }
            if notes is not None:
                payload["mood"]["notes"] = notes

        try:
            await client.async_post("/fasting/end", json=payload)
            await coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to end fast: {err}") from err

    async def handle_log_water(call):
        """Handle log water service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Sparky Fitness integration not configured")
        entry = entries[0]
        client = entry.runtime_data.client
        coordinator = entry.runtime_data.coordinator

        amount_ml = call.data.get("amount_ml")
        drinks = call.data.get("drinks")
        container_input = call.data.get("container")

        containers = coordinator.data.get("water_containers", [])
        selected_container = None

        if container_input:
            # Try UUID match first
            for c in containers:
                if c.get("id") == container_input:
                    selected_container = c
                    break
            # Try name match next
            if not selected_container:
                for c in containers:
                    if c.get("name", "").lower() == container_input.lower():
                        selected_container = c
                        break

        if not selected_container:
            # Fallback to primary container
            for c in containers:
                if c.get("is_primary"):
                    selected_container = c
                    break
            # Fallback to first container
            if not selected_container and containers:
                selected_container = containers[0]

        if not selected_container:
            raise HomeAssistantError("No water container defined in Sparky Fitness")

        if drinks is not None:
            change_drinks = float(drinks)
        else:
            # Calculate volume in ml
            unit = str(selected_container.get("unit", "ml")).lower()
            volume = float(selected_container.get("volume", 250.0))
            if "oz" in unit:
                container_volume_ml = volume * 29.5735
            else:
                container_volume_ml = volume

            if container_volume_ml <= 0:
                raise HomeAssistantError("Container volume must be greater than zero")

            change_drinks = round(float(amount_ml) / container_volume_ml, 2)

        today = dt_util.now().date().isoformat()

        payload = {
            "entry_date": today,
            "change_drinks": change_drinks,
            "container_id": selected_container["id"],
        }

        try:
            await client.async_post("/measurements/water-intake", json=payload)
            await coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to log water intake: {err}") from err

    async def handle_log_mood(call):
        """Handle log mood service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Sparky Fitness integration not configured")
        entry = entries[0]
        client = entry.runtime_data.client
        coordinator = entry.runtime_data.coordinator

        mood_value = call.data["mood_value"]
        notes = call.data.get("notes")
        today = dt_util.now().date().isoformat()

        payload = {
            "mood_value": mood_value,
            "entry_date": today,
        }
        if notes is not None:
            payload["notes"] = notes

        try:
            await client.async_post("/mood", json=payload)
            await coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to log mood: {err}") from err

    async def handle_log_check_in(call):
        """Handle log check-in service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Sparky Fitness integration not configured")
        entry = entries[0]
        client = entry.runtime_data.client
        coordinator = entry.runtime_data.coordinator

        weight = call.data.get("weight")
        body_fat = call.data.get("body_fat")
        today = dt_util.now().date().isoformat()

        payload = {
            "entry_date": today,
        }
        if weight is not None:
            payload["weight"] = weight
        if body_fat is not None:
            payload["body_fat_percentage"] = body_fat

        try:
            await client.async_post("/measurements/check-in", json=payload)
            await coordinator.async_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to log check-in: {err}") from err

    if not hass.services.has_service(DOMAIN, "start_fast"):
        hass.services.async_register(DOMAIN, "start_fast", handle_start_fast, schema=START_FAST_SCHEMA)
        hass.services.async_register(DOMAIN, "end_fast", handle_end_fast, schema=END_FAST_SCHEMA)
        hass.services.async_register(DOMAIN, "log_water", handle_log_water, schema=LOG_WATER_SCHEMA)
        hass.services.async_register(DOMAIN, "log_mood", handle_log_mood, schema=LOG_MOOD_SCHEMA)
        hass.services.async_register(DOMAIN, "log_check_in", handle_log_check_in, schema=LOG_CHECK_IN_SCHEMA)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SparkyFitnessConfigEntry) -> bool:
    """Unload a SparkyFitness config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        entries = hass.config_entries.async_entries(DOMAIN)
        remaining_entries = [e for e in entries if e.entry_id != entry.entry_id]
        if not remaining_entries:
            for service in ["start_fast", "end_fast", "log_water", "log_mood", "log_check_in"]:
                if hass.services.has_service(DOMAIN, service):
                    hass.services.async_remove(DOMAIN, service)
    return unload_ok
