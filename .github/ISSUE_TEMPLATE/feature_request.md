---
name: Feature Request
about: Suggest a new feature or improvement
labels: enhancement
---

## Summary

A brief, one-sentence description of the feature request.

## Description

> **User Story (optional):** As a user, I want **[this behavior]**, so that **[this outcome]** is achieved.

Describe the feature in detail and explain the use case. How would this improve your WallPanel experience?

## Current Behavior

What are the current limitations?

- What can't you do with the current integration?
- Are there workarounds, but they're complex or unreliable?
- Is this related to WallPanel REST API capabilities or integration features?

## Proposed Solution

How would you like this feature to work? Be as specific as possible.

### Example: Desired Configuration

```yaml
# Example of how you'd like to configure this feature
media_player:
  - platform: wallpanel_media_player
    name: Wallpanel Media Player
    address: http://192.168.1.100:2971
    new_option: value
    # Add proposed configuration options
```

### Example: Service Call

```yaml
# How you'd like to use this feature
service: media_player.new_service
target:
  entity_id: media_player.wallpanel_media_player
data:
  parameter: value
```

### Example: Expected Behavior

What should happen when this feature is used?

- Entity state changes
- Device actions
- Attributes exposed

## WallPanel REST API Support

- [ ] This feature is supported by WallPanel REST API
- [ ] I've tested this via direct API calls (curl/Postman)
- [ ] WallPanel app version: ___________
- [ ] API endpoint: `POST/GET /api/...`

<details>
<summary>API test results (if applicable)</summary>

```bash
# Example curl command and response
curl -X POST http://192.168.1.100:2971/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "..."}'
```

</details>

## Alternatives Considered

Have you considered any alternative approaches or workarounds?

- Custom scripts or automations?
- Other integrations or tools?
- Manual controls via WallPanel app?

## Use Case / Benefits

Who would benefit from this feature and how?

- Personal use case description
- Potential benefits for other users
- Impact on Home Assistant dashboards or automations
- Enhancement to WallPanel device management

## Additional Context

Add any other context, or links about the feature request here.