"""Text platform for Google Home."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator 
from homeassistant.helpers.entity import Entity, EntityCategory

from .const import (
    DATA_CLIENT,
    DATA_COORDINATOR,
    DOMAIN,
    ICON_TOKEN,
)
from .entity import GoogleHomeBaseEntity
from .models import GoogleHomeDevice
from .api import GlocaltokensApiClient 

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import (
        GoogleHomeConfigEntry
    )
_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GoogleHomeConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> bool:
    """Set up sensor platform."""
    client: GlocaltokensApiClient = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    coordinator: DataUpdateCoordinator[list[GoogleHomeDevice]] = hass.data[DOMAIN][
        entry.entry_id
    ][DATA_COORDINATOR]
    entities: list[Entity] = []
    for device in coordinator.data:
        # Add the IP address text entity
        entities.append(
            GoogleHomeIpAddressTextEntity(
                coordinator,
                client,
                device.device_id,
                device.name,
                device.hardware,
            )
        )
    async_add_devices(entities)

    return True


class GoogleHomeIpAddressTextEntity(GoogleHomeBaseEntity, TextEntity):
    """Text entity to edit the IP address of a Google Home device."""

    _attr_mode = TextMode.TEXT
    _attr_icon = ICON_TOKEN
    _attr_entity_category: str = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[list[GoogleHomeDevice]],
        client: GlocaltokensApiClient,
        device_id: str,
        device_name: str,
        device_model: str,
    ) -> None:
        """Initialize the IP address text entity."""
        super().__init__(coordinator, client, device_id, device_name, device_model)
        self._attr_name: str = f"IP Address"
        self._attr_unique_id: str = f"{self.device_id}_ip_address"
        self._attr_native_value: str = self._get_ip_address()

    @property
    def label(self) -> str:
        """Label to use for name and unique id."""
        return "IP Address"

    @property
    def native_value(self) -> str:
        """Return the current IP address."""
        return self.state()
    
    @property
    def state(self) -> str | None:  # type: ignore[override]
        """Return the current IP address."""
        return self._get_ip_address()

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional attributes."""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "editable": "true",
        }
    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return whether the entity should be enabled by default."""
        return True

    def _get_ip_address(self) -> str:
        """Retrieve the current IP address from the device."""
        device = self.get_device()
        return device.ip_address if device and device.ip_address else "Unknown"

    async def async_set_value(self, value: str) -> None:
        """Set the IP address."""
        # Update the IP address using the API client
        await self.client.update_device_ip_address(self.get_device(), value)
        
