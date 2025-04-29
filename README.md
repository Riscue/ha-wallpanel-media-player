# Wallpanel Media Player

[https://wallpanel.xyz](https://wallpanel.xyz)

![Icon](assets/logo.png)

## Installation

1. Copy the wallpanel_media_player folder to your custom_components folder in your Home Assistant configuration.
2. Add the integration via configuration.yaml
3. Restart Home Assistant.

### Example configuration

```
media_player:
  - platform: wallpanel_media_player
    name: Wallpanel Media Player
    address: http://127.0.0.1:2971
```
