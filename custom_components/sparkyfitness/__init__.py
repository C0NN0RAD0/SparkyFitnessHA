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
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_TIMEOUT_SECONDS, DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class SparkyFitnessConfig:
    """Config data used by the API client."""

    host: str
    token: str


class SparkyFitnessApiClient:
    """Simple async API client for SparkyFitness endpoints."""

    def __init__(self, session: ClientSession, config: SparkyFitnessConfig) -> None:
        self._session = session
        self._host = config.host.rstrip("/")
        self._token = config.token

    async def async_get(self, endpoint: str) -> dict[str, Any]:
        """GET JSON from a SparkyFitness API endpoint."""
        url = f"{self._host}/api{endpoint}"
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

        if isinstance(payload, dict):
            return payload

        return {}


@dataclass
class SparkyFitnessRuntimeData:
    """Runtime data attached to each config entry."""

    client: SparkyFitnessApiClient
    coordinator: DataUpdateCoordinator[dict[str, Any]]


SparkyFitnessConfigEntry: TypeAlias = ConfigEntry[SparkyFitnessRuntimeData]


async def _async_update_data(client: SparkyFitnessApiClient) -> dict[str, Any]:
    """Fetch all datasets used by entities."""
    data: dict[str, Any] = {
        "daily_summary": {},
        "measurements": [],
        "sleep": {},
        "exercises": [],
        "water": {},
        "mood": {},
    }

    endpoints = {
        "daily_summary": "/daily-summary",
        "measurements": "/measurements?limit=1",
        "sleep": "/sleep?limit=1",
        "exercises": "/exercise-entries?limit=10",
        "water": "/water-containers",
        "mood": "/mood?limit=1",
    }

    for key, endpoint in endpoints.items():
        try:
            response = await client.async_get(endpoint)
        except ClientResponseError as err:
            if err.status == 401:
                raise UpdateFailed("Authentication failed") from err
            raise UpdateFailed(f"API error for {endpoint}: HTTP {err.status}") from err
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Unexpected update error: {err}") from err

        if key == "measurements":
            data[key] = response.get("measurements", [])
        elif key == "exercises":
            data[key] = response.get("exercises", [])
        else:
            data[key] = response

    return data


async def async_setup_entry(hass: HomeAssistant, entry: SparkyFitnessConfigEntry) -> bool:
    """Set up SparkyFitness from a config entry."""
    session = async_get_clientsession(hass)
    config = SparkyFitnessConfig(
        host=entry.data[CONF_HOST],
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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SparkyFitnessConfigEntry) -> bool:
    """Unload a SparkyFitness config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
