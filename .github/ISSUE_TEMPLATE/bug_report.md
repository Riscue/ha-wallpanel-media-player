---
name: Bug Report
about: Report a problem or unexpected behavior
labels: bug
---

## Description

A clear and concise description of the bug.

## To Reproduce

Steps to reproduce the behavior:

1. Configure integration with '...'
2. Try to play media / control device '...'
3. Call service '...'
4. See error in logs / UI

## Actual Behavior

What actually happened? Include error messages if available.

## Expected Behavior

What you expected to happen instead.

## Environment

| Component                                      | Version / Info                |
|------------------------------------------------|-------------------------------|
| Home Assistant Core                            | e.g. 2025.1.3                 |
| WallPanel App Version                          | e.g. 0.9.x                    |
| Device Type                                    | e.g. Android Tablet / Fire TV |
| Device Android Version                         | e.g. 13                       |
| Integration Version (`wallpanel_media_player`) | e.g. 1.0.0                    |
| Installation Method                            | HACS / Manual                 |

## Configuration

```yaml
# Configuration from configuration.yaml
media_player:
  - platform: wallpanel_media_player
    name: Wallpanel Media Player
    address: http://192.168.1.100:2971
    # Add other relevant config
```

## Network Configuration

- WallPanel device IP: `192.168.1.xxx`
- Home Assistant IP: `192.168.1.xxx`
- Are both on the same network/VLAN? Yes / No
- Can you ping WallPanel device from HA server? Yes / No / Not tested

## Logs

<details>
<summary>Home Assistant logs (click to expand)</summary>

```
Paste relevant logs from Home Assistant (Configuration > Logs or home-assistant.log)
Filter by 'wallpanel_media_player' if possible
```

</details>

## Service Call / Action Attempted

Which media player service were you trying to use?

- [ ] media_player.play_media
- [ ] media_player.volume_set
- [ ] media_player.media_stop
- [ ] Other (specify): ___________

```yaml
# Service call that failed
target:
  entity_id: media_player.wallpanel_media_player
data:
  media:
    media_content_id: http://example.com/audio.mp3
    media_content_type: url
    metadata: {}
action: media_player.play_media
```

## Additional Context

- Does the WallPanel app respond to manual controls?
- Can you access WallPanel REST API directly (e.g., via curl or browser)?
- Did this work in a previous version?
- Any recent changes to network, firewall, or app permissions?
- Is the device experiencing any performance issues?
- ...

Add any other context about the problem here.