"""Set up the Wallpanel Media Player component."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "wallpanel_media_player"
PLATFORMS = [Platform.MEDIA_PLAYER]
DATA_CONFIG_ENTRY = "config_entry"
DATA_HASS_CONFIG = "hass_config"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the LG WebOS TV platform."""
    print("__init__async_setup")
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_CONFIG_ENTRY, {})
    hass.data[DOMAIN][DATA_HASS_CONFIG] = config

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set the config entry up."""
    print("__init__async_setup_entry")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
