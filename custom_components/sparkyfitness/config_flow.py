"""Config flow for SparkyFitness integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from aiohttp import ClientError
import async_timeout

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_TIMEOUT_SECONDS, CONF_SCHEME, CONF_VERIFY_SSL, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_SCHEME, default="https"): vol.In(["https"]),
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_TOKEN): str,
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
    }
)


class SparkyFitnessConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SparkyFitness."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._async_validate_input(user_input)
            except InvalidAuthError:
                errors["base"] = "invalid_auth"
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_SCHEME: user_input[CONF_SCHEME],
                        CONF_HOST: user_input[CONF_HOST].rstrip("/"),
                        CONF_TOKEN: user_input[CONF_TOKEN],
                        CONF_VERIFY_SSL: user_input[CONF_VERIFY_SSL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _async_validate_input(self, user_input: dict[str, Any]) -> None:
        """Validate host and token by calling health endpoint."""
        session = async_get_clientsession(
            self.hass, verify_ssl=user_input[CONF_VERIFY_SSL]
        )
        url = f"https://{user_input[CONF_HOST].rstrip('/')}/api/health"
        headers = {"Authorization": f"Bearer {user_input[CONF_TOKEN]}"}

        try:
            async with async_timeout.timeout(API_TIMEOUT_SECONDS):
                async with session.get(url, headers=headers) as response:
                    if response.status == 401:
                        raise InvalidAuthError

                    if response.status >= 400:
                        raise CannotConnectError

                    await response.read()
        except InvalidAuthError:
            raise
        except (ClientError, TimeoutError):
            raise CannotConnectError


class CannotConnectError(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuthError(Exception):
    """Error to indicate authentication failure."""
