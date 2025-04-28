"""Wallpanel media player component."""

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.media_player import (
    PLATFORM_SCHEMA as MEDIA_PLAYER_PLATFORM_SCHEMA,
)
from homeassistant.const import CONF_NAME, CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from custom_components.wallpanel_media_player.wallpanel import WallpanelMediaPlayer

_LOGGER = logging.getLogger(__name__)

CONF_ARGUMENTS = "arguments"
DEFAULT_NAME = "Wallpanel Media Player"

PLATFORM_SCHEMA = MEDIA_PLAYER_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_ADDRESS, default="http://127.0.0.1:2971"): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Wallpanel Media Player platform."""
    add_entities(
        [WallpanelMediaPlayer(config.get(CONF_NAME, DEFAULT_NAME), config.get(CONF_ADDRESS))]
    )
