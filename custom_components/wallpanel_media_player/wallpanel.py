import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any

import requests
from homeassistant.components import media_source
from homeassistant.components.media_player import MediaPlayerEntity, MediaType, MediaPlayerEntityFeature, \
    MediaPlayerState, async_process_play_media_url
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

HEADERS = {"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}
TIMEOUT = 5
MAX_RETRIES = 3
RETRY_DELAY = 1


class WallpanelMediaPlayer(MediaPlayerEntity):
    """Representation of a Wallpanel Media Player."""
    _attr_supported_features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.PLAY_MEDIA
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
    )

    def __init__(self, name, address):
        _LOGGER.debug("WallpanelMediaPlayer Init: name: %s, address: %s", name, address)
        self._attr_name = name
        self._attr_state = MediaPlayerState.IDLE
        self._attr_volume_level = 0.5
        self._address = address

        # Media tracking attributes
        self._attr_media_duration = None
        self._attr_media_position = None
        self._attr_media_position_updated_at = None
        self._current_media_url = None
        self._attr_media_content_type = MediaType.MUSIC
        self._is_available = True

    def set_volume_level(self, volume: float) -> None:
        self._attr_volume_level = volume
        self.send_command({"volume": int(self._attr_volume_level * 100)})

    def media_stop(self) -> None:
        self._attr_state = MediaPlayerState.IDLE
        self._attr_media_duration = None
        self._attr_media_position = None
        self._attr_media_position_updated_at = None
        self._current_media_url = None
        self.send_command({"audio": ""})
        self.async_write_ha_state()

    async def async_play_media(
            self, media_type: MediaType | str, media_id: str, **kwargs: Any
    ) -> None:
        """Play media from a URL or file."""
        # Handle media_source
        if media_source.is_media_source_id(media_id):
            sourced_media = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = sourced_media.url

        elif media_type != MediaType.MUSIC:
            _LOGGER.error(
                "Invalid media type %s. Only %s is supported",
                media_type,
                MediaType.MUSIC,
            )
            return

        media_id = async_process_play_media_url(self.hass, media_id)

        def play():
            self._attr_state = MediaPlayerState.PLAYING
            self._current_media_url = media_id
            self._attr_media_position = 0
            self._attr_media_position_updated_at = datetime.utcnow()
            # Reset duration as we don't get this info from Wallpanel API
            self._attr_media_duration = None

            # Update media content type
            if hasattr(media_type, 'value'):
                self._attr_media_content_type = media_type
            else:
                self._attr_media_content_type = media_type

            self.send_command({"volume": int(self._attr_volume_level * 100), "audio": media_id})
            self.async_write_ha_state()

        await self.hass.async_add_executor_job(play)

    async def async_speak(self, text: str) -> None:
        """Speak text using device TTS."""
        def speak_command():
            self.send_command({"speak": text})

        await self.hass.async_add_executor_job(speak_command)

    def turn_on(self) -> None:
        """Turn the media player on."""
        self._attr_state = MediaPlayerState.IDLE
        self._is_available = True
        self.async_write_ha_state()

    def turn_off(self) -> None:
        """Turn the media player off."""
        self._attr_state = MediaPlayerState.OFF
        self._is_available = False
        self.async_write_ha_state()

    @property
    def media_position(self) -> int | None:
        """Position of current media in seconds."""
        return self._attr_media_position

    @property
    def media_position_updated_at(self) -> datetime | None:
        """When was the position of the current media valid."""
        return self._attr_media_position_updated_at

    @property
    def media_duration(self) -> float | None:
        """Duration of current media in seconds."""
        return self._attr_media_duration

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._is_available

    @property
    def assumed_state(self) -> bool:
        """Return True if we cannot track the state of the device."""
        return False

    @callback
    def _update_connection_state(self, success: bool) -> None:
        """Update connection state based on command success."""
        was_available = self._is_available
        self._is_available = success

        if was_available != self._is_available:
            if self._is_available:
                self._attr_state = MediaPlayerState.IDLE
            else:
                self._attr_state = MediaPlayerState.OFF
            self.async_write_ha_state()

    def send_command(self, payload, retry_count=0):
        """Send command to wallpanel with retry logic."""
        url = f"{self._address}/api/command"
        _LOGGER.debug("Sending command: %s -> %s", url, payload)

        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            _LOGGER.debug("Command sent successfully: %s", payload)
            self._update_connection_state(True)
            return True

        except requests.exceptions.ConnectionError as err:
            _LOGGER.warning("Connection error to Wallpanel: %s", err)
            if retry_count < MAX_RETRIES:
                _LOGGER.info("Retrying command in %d seconds (attempt %d/%d)",
                           RETRY_DELAY, retry_count + 1, MAX_RETRIES)
                time.sleep(RETRY_DELAY)
                return self.send_command(payload, retry_count + 1)
            else:
                _LOGGER.error("Max retries reached for Wallpanel command: %s", err)
                self._update_connection_state(False)
                raise HomeAssistantError(f"Failed to connect to Wallpanel after {MAX_RETRIES} attempts: {err}")

        except requests.exceptions.Timeout as err:
            _LOGGER.warning("Timeout sending command to Wallpanel: %s", err)
            if retry_count < MAX_RETRIES:
                _LOGGER.info("Retrying command due to timeout (attempt %d/%d)",
                           retry_count + 1, MAX_RETRIES)
                time.sleep(RETRY_DELAY)
                return self.send_command(payload, retry_count + 1)
            else:
                _LOGGER.error("Command timed out after %d attempts: %s", MAX_RETRIES, err)
                self._update_connection_state(False)
                raise HomeAssistantError(f"Wallpanel command timed out after {MAX_RETRIES} attempts: {err}")

        except requests.exceptions.HTTPError as err:
            status_code = getattr(err.response, 'status_code', 'unknown')
            _LOGGER.error("HTTP error from Wallpanel: %s (status: %s)", err, status_code)
            self._update_connection_state(False)
            raise HomeAssistantError(f"Wallpanel returned HTTP {status_code}: {err}")

        except Exception as err:
            _LOGGER.error("Unexpected error sending command to Wallpanel: %s", err)
            self._update_connection_state(False)
            raise HomeAssistantError(f"Unexpected error with Wallpanel: {err}")
