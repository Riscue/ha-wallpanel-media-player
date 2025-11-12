"""Configuration for pytest."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def hass():
    """Mock Home Assistant fixture."""
    hass = Mock()
    hass.async_add_executor_job = Mock()
    return hass


@pytest.fixture
def mock_hass():
    """Mock Home Assistant with async methods."""
    hass = Mock()
    hass.async_add_executor_job = Mock()
    hass.async_create_task = Mock()
    return hass