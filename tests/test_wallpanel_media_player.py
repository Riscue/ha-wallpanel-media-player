"""Tests for the Wallpanel Media Player integration."""

import json
import pytest
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime

from homeassistant.components.media_player import (
    MediaPlayerState,
    MediaPlayerEntityFeature,
    MediaType,
)
from homeassistant.const import CONF_NAME, CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
import requests

from custom_components.wallpanel_media_player.media_player import PLATFORM_SCHEMA, setup_platform
from custom_components.wallpanel_media_player.wallpanel import WallpanelMediaPlayer


class TestWallpanelMediaPlayer:
    """Test WallpanelMediaPlayer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.name = "Test Wallpanel"
        self.address = "http://127.0.0.1:2971"
        self.player = WallpanelMediaPlayer(self.name, self.address)
        # Mock async_write_ha_state to prevent hass None errors
        self.player.async_write_ha_state = Mock()

    def test_init(self):
        """Test initialization."""
        assert self.player.name == self.name
        assert self.player._address == self.address
        assert self.player.state == MediaPlayerState.IDLE
        assert self.player.volume_level == 0.5
        assert self.player.available is True
        assert self.player.media_content_type == MediaType.MUSIC

    def test_supported_features(self):
        """Test supported features."""
        expected_features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.PLAY_MEDIA
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
        )
        assert self.player.supported_features == expected_features

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_set_volume_level(self, mock_post):
        """Test setting volume level."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.player.set_volume_level(0.75)

        assert self.player.volume_level == 0.75
        mock_post.assert_called_once_with(
            f"{self.address}/api/command",
            data=json.dumps({"volume": 75}),
            headers={"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"},
            timeout=5,
        )

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_media_stop(self, mock_post):
        """Test media stop."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.player.media_stop()

        assert self.player.state == MediaPlayerState.IDLE
        assert self.player.media_position is None
        assert self.player.media_position_updated_at is None
        assert self.player.media_duration is None
        mock_post.assert_called_once_with(
            f"{self.address}/api/command",
            data=json.dumps({"audio": ""}),
            headers={"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"},
            timeout=5,
        )

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    @patch("custom_components.wallpanel_media_player.wallpanel.async_process_play_media_url")
    async def test_async_play_media(self, mock_process_url, mock_post):
        """Test async play media."""
        mock_process_url.return_value = "http://example.com/test.mp3"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock hass and async_add_executor_job
        hass = Mock()
        hass.async_add_executor_job = AsyncMock()
        self.player.hass = hass
        self.player.async_write_ha_state = Mock()

        await self.player.async_play_media(MediaType.MUSIC, "test.mp3")

        mock_process_url.assert_called_once_with(hass, "test.mp3")
        hass.async_add_executor_job.assert_called_once()

    @patch("custom_components.wallpanel_media_player.wallpanel.media_source.is_media_source_id")
    @patch("custom_components.wallpanel_media_player.wallpanel.media_source.async_resolve_media")
    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    @patch("custom_components.wallpanel_media_player.wallpanel.async_process_play_media_url")
    async def test_async_play_media_source(self, mock_process_url, mock_post, mock_resolve, mock_is_media):
        """Test async play media with media source."""
        mock_is_media.return_value = True
        mock_resolve.return_value = Mock(url="http://resolved.media.url")
        mock_process_url.return_value = "http://processed.media.url"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock hass and async_add_executor_job
        hass = Mock()
        hass.async_add_executor_job = AsyncMock()
        self.player.hass = hass
        self.player.async_write_ha_state = Mock()
        self.player.entity_id = "media_player.test"

        await self.player.async_play_media(MediaType.MUSIC, "media_source://test")

        mock_is_media.assert_called_once_with("media_source://test")
        mock_resolve.assert_called_once_with(hass, "media_source://test", "media_player.test")
        mock_process_url.assert_called_once_with(hass, "http://resolved.media.url")
        hass.async_add_executor_job.assert_called_once()

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    @patch("custom_components.wallpanel_media_player.wallpanel.async_process_play_media_url")
    async def test_async_play_media_string_type(self, mock_process_url, mock_post):
        """Test async play media with string media type."""
        mock_process_url.return_value = "http://example.com/test.mp3"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock hass and async_add_executor_job
        hass = Mock()
        hass.async_add_executor_job = AsyncMock()
        self.player.hass = hass
        self.player.async_write_ha_state = Mock()

        await self.player.async_play_media("music", "test.mp3")

        mock_process_url.assert_called_once_with(hass, "test.mp3")
        hass.async_add_executor_job.assert_called_once()

        # Verify media content type is set to string
        assert self.player.media_content_type == "music"

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    @patch("custom_components.wallpanel_media_player.wallpanel.async_process_play_media_url")
    async def test_async_play_media_invalid_type(self, mock_process_url, mock_post):
        """Test async play media with invalid media type."""
        # Mock hass and async_add_executor_job
        hass = Mock()
        hass.async_add_executor_job = AsyncMock()
        self.player.hass = hass

        await self.player.async_play_media(MediaType.VIDEO, "test.mp4")

        mock_post.assert_not_called()
        hass.async_add_executor_job.assert_not_called()
        # State should not change for invalid media type
        assert self.player.state == MediaPlayerState.IDLE

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    async def test_async_speak(self, mock_post):
        """Test async speak TTS."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock hass and async_add_executor_job
        hass = Mock()
        hass.async_add_executor_job = AsyncMock()
        self.player.hass = hass

        await self.player.async_speak("Hello world")

        hass.async_add_executor_job.assert_called_once()

    def test_turn_on(self):
        """Test turn on."""
        self.player.async_write_ha_state = Mock()

        # Set initial state to OFF
        self.player._attr_state = MediaPlayerState.OFF
        self.player._is_available = False

        self.player.turn_on()

        assert self.player.state == MediaPlayerState.IDLE
        assert self.player.available is True
        self.player.async_write_ha_state.assert_called_once()

    def test_turn_on_when_already_on(self):
        """Test turn on when already on (should still call state update)."""
        self.player.async_write_ha_state = Mock()

        # Set initial state to already ON
        self.player._attr_state = MediaPlayerState.IDLE
        self.player._is_available = True

        self.player.turn_on()

        assert self.player.state == MediaPlayerState.IDLE
        assert self.player.available is True
        # Should still call async_write_ha_state to sync state
        self.player.async_write_ha_state.assert_called_once()

    def test_turn_off(self):
        """Test turn off."""
        self.player.async_write_ha_state = Mock()

        self.player.turn_off()

        assert self.player.state == MediaPlayerState.OFF
        assert self.player.available is False
        self.player.async_write_ha_state.assert_called_once()

    def test_media_position_properties(self):
        """Test media position related properties."""
        assert self.player.media_position is None
        assert self.player.media_position_updated_at is None
        assert self.player.media_duration is None

    def test_available_property(self):
        """Test available property."""
        assert self.player.available is True

    def test_assumed_state_property(self):
        """Test assumed_state property."""
        assert self.player.assumed_state is False


class TestSendCommand:
    """Test send_command method with error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.name = "Test Wallpanel"
        self.address = "http://127.0.0.1:2971"
        self.player = WallpanelMediaPlayer(self.name, self.address)
        self.player.async_write_ha_state = Mock()

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_send_command_success(self, mock_post):
        """Test successful command sending."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.player.send_command({"test": "command"})

        assert result is True
        mock_post.assert_called_once()
        # async_write_ha_state should not be called when connection state doesn't change

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    @patch("custom_components.wallpanel_media_player.wallpanel.time.sleep")
    def test_send_command_retry_on_connection_error(self, mock_sleep, mock_post):
        """Test retry logic on connection error."""
        mock_post.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
        ]

        with pytest.raises(HomeAssistantError):
            self.player.send_command({"test": "command"})

        # Should be called 4 times (initial + 3 retries)
        assert mock_post.call_count == 4
        assert mock_sleep.call_count == 3
        # Verify connection state updated to unavailable
        assert self.player.available is False
        assert self.player.state == MediaPlayerState.OFF

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    @patch("custom_components.wallpanel_media_player.wallpanel.time.sleep")
    def test_send_command_retry_on_timeout(self, mock_sleep, mock_post):
        """Test retry logic on timeout."""
        mock_response_success = Mock()
        mock_response_success.raise_for_status.return_value = None

        mock_post.side_effect = [
            requests.exceptions.Timeout("Request timeout"),
            mock_response_success,
        ]

        result = self.player.send_command({"test": "command"})

        assert result is True
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_send_command_http_error(self, mock_post):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response

        with pytest.raises(HomeAssistantError):
            self.player.send_command({"test": "command"})

        mock_post.assert_called_once()
        # Verify connection state updated to unavailable
        assert self.player.available is False

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_send_command_http_error_no_response(self, mock_post):
        """Test HTTP error handling with response but no status_code."""
        # Create a response without status_code attribute
        mock_response = Mock()
        del mock_response.status_code  # Remove status_code attribute

        http_error = requests.exceptions.HTTPError("HTTP Error without status code")
        http_error.response = mock_response

        mock_post.side_effect = http_error

        with pytest.raises(HomeAssistantError):
            self.player.send_command({"test": "command"})

        mock_post.assert_called_once()
        # Verify connection state updated to unavailable
        assert self.player.available is False

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_send_command_general_error(self, mock_post):
        """Test general error handling."""
        mock_post.side_effect = Exception("Unexpected error")

        with pytest.raises(HomeAssistantError):
            self.player.send_command({"test": "command"})

        mock_post.assert_called_once()


class TestSetupPlatform:
    """Test platform setup."""

    def test_setup_platform(self):
        """Test platform setup."""
        hass = Mock()
        add_entities = Mock()

        config = {
            CONF_NAME: "Test Wallpanel",
            CONF_ADDRESS: "http://127.0.0.1:2971"
        }

        setup_platform(hass, config, add_entities)

        add_entities.assert_called_once()
        args = add_entities.call_args[0][0]
        assert len(args) == 1
        assert isinstance(args[0], WallpanelMediaPlayer)
        assert args[0].name == "Test Wallpanel"
        assert args[0]._address == "http://127.0.0.1:2971"

    def test_setup_platform_with_defaults(self):
        """Test platform setup with default values."""
        hass = Mock()
        add_entities = Mock()

        config = {}  # Use defaults

        setup_platform(hass, config, add_entities)

        add_entities.assert_called_once()
        args = add_entities.call_args[0][0]
        assert isinstance(args[0], WallpanelMediaPlayer)
        assert args[0].name == "Wallpanel Media Player"  # default name
        assert args[0]._address == "http://127.0.0.1:2971"  # default address


class TestConnectionState:
    """Test connection state management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.player = WallpanelMediaPlayer("Test", "http://127.0.0.1:2971")
        self.player.async_write_ha_state = Mock()

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_connection_state_success(self, mock_post):
        """Test connection state on successful command."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.player.send_command({"test": "command"})

        assert self.player.available is True
        assert self.player.state == MediaPlayerState.IDLE

    @patch("custom_components.wallpanel_media_player.wallpanel.requests.post")
    def test_connection_state_failure(self, mock_post):
        """Test connection state on failed command."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        try:
            self.player.send_command({"test": "command"})
        except HomeAssistantError:
            pass

        assert self.player.available is False
        assert self.player.state == MediaPlayerState.OFF