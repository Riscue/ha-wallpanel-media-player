import json
import logging
import time
from typing import Any

import requests
from homeassistant.components import media_source
from homeassistant.components.media_player import MediaPlayerEntity, MediaType, MediaPlayerEntityFeature, \
    MediaPlayerState, async_process_play_media_url
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

HEADERS = {"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}
TIMEOUT = 5
MAX_RETRIES = 3
RETRY_DELAY = 1


class WallpanelMediaPlayer(MediaPlayerEntity):
    """Representation of a Wallpanel Media Player."""

    _attr_media_content_type = MediaType.MUSIC
    _attr_supported_features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.PLAY_MEDIA
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.SPEAK
    )

    def __init__(self, name, address):
        _LOGGER.debug("WallpanelMediaPlayer Init: name: %s, address: %s", name, address)
        self._attr_name = name
        self._attr_state = MediaPlayerState.ON
        self._attr_volume_level = 0.5
        self._address = address

    def set_volume_level(self, volume: float) -> None:
        self._attr_volume_level = volume
        self.send_command({"volume": int(self._attr_volume_level * 100)})

    def media_stop(self) -> None:
        self.send_command({"audio": ""})

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
            self.send_command({"volume": int(self._attr_volume_level * 100), "audio": media_id})

        await self.hass.async_add_executor_job(play)

    async def async_speak(self, text: str) -> None:
        """Speak text using device TTS."""
        def speak_command():
            self.send_command({"speak": text})

        await self.hass.async_add_executor_job(speak_command)

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
                raise HomeAssistantError(f"Failed to connect to Wallpanel after {MAX_RETRIES} attempts: {err}")

        except requests.exceptions.Timeout as err:
            _LOGGER.warning("Timeout sending command to Wallpanel: %s", err)
            if retry_count < MAX_RETRIES:
                _LOGGER.info("Retrying command due to timeout (attempt %d/%d)",
                           retry_count + 1, MAX_RETRIES)
                return self.send_command(payload, retry_count + 1)
            else:
                _LOGGER.error("Command timed out after %d attempts: %s", MAX_RETRIES, err)
                raise HomeAssistantError(f"Wallpanel command timed out after {MAX_RETRIES} attempts: {err}")

        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            _LOGGER.error("HTTP error from Wallpanel: %s (status: %d)", err, status_code)
            raise HomeAssistantError(f"Wallpanel returned HTTP {status_code}: {err}")

        except Exception as err:
            _LOGGER.error("Unexpected error sending command to Wallpanel: %s", err)
            raise HomeAssistantError(f"Unexpected error with Wallpanel: {err}")
