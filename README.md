# Wallpanel Media Player

[![Home Assistant](https://img.shields.io/badge/home%20assistant-%2341BDF5.svg?style=for-the-badge&logo=home-assistant&logoColor=white)](https://home-assistant.io)
[![hacs](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![License][license-shield]](LICENSE.md)

[license-shield]: https://img.shields.io/github/license/Riscue/ha-wallpanel-media-player.svg?style=for-the-badge

[![GitHub Release](https://img.shields.io/github/release/Riscue/ha-wallpanel-media-player.svg?style=for-the-badge)](https://github.com/Riscue/ha-wallpanel-media-player/releases)
[![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/Riscue/ha-wallpanel-media-player/latest/total?label=downloads&style=for-the-badge)](https://github.com/Riscue/ha-wallpanel-media-player/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Riscue/ha-wallpanel-media-player.svg?style=for-the-badge)](https://github.com/Riscue/ha-wallpanel-media-player/commits/master)

Media Player integration for [https://wallpanel.xyz](https://wallpanel.xyz)

![Icon](assets/logo.png)

## Installation

### HACS Installation (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Riscue&repository=ha-wallpanel-media-player)

### Manual Installation

1. Copy the wallpanel_media_player folder to your custom_components folder in your Home Assistant configuration.
2. Add the integration via configuration.yaml
3. Restart Home Assistant.

## Example configuration

```
media_player:
  - platform: wallpanel_media_player
    name: Wallpanel Media Player
    address: http://127.0.0.1:2971
```

## License

MIT © [Riscue](https://github.com/riscue)
