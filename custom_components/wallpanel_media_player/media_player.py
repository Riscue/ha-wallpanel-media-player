import logging
import requests
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.const import STATE_IDLE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the LG webOS Smart TV platform."""
    print("media_player_async_setup_entry")
    async_add_entities([WallpanelMediaPlayer(entry)])


class WallpanelMediaPlayer(MediaPlayerEntity):
    """Representation of a Wallpanel media player."""

    def __init__(self, entry: ConfigEntry):
        print("WallpanelMediaPlayer__init__")
        self._name = entry.name
        self._address = entry.address
        self._state = STATE_IDLE
        self._volume = 1.0

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def volume_level(self):
        return self._volume

    def set_volume_level(self, volume):
        """Set volume level of the Wallpanel."""
        self._volume = volume
        self.send_audio_command("volume", volume)

    def media_play(self):
        """Play the media."""
        self.send_audio_command("audio")

    def media_stop(self):
        """Stop the media."""
        self.send_audio_command("audio", "stop")

    def send_audio_command(self, command, value=None):
        """Send an audio command to Wallpanel."""
        url = f"{self._address}/api/command"
        payload = {command: value} if value else {command: True}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error sending command to Wallpanel: %s", err)
