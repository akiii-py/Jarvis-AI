# JARVIS App Navigation System

## Overview

The App Navigation System enables JARVIS to control applications beyond just opening them. It can search, play music, send messages, and navigate websites through natural language commands.

## Architecture

```
User Command → AppNavigator → Specific Controller → macOS Accessibility APIs → App Control
```

### Components

1. **`element_finder.py`** - Core accessibility helper
   - Type text, press keys, activate apps
   - Uses AppleScript via `osascript`

2. **`spotify_controller.py`** - Music control
   - Search and play songs/playlists
   - Playback control (pause, next, previous)

3. **`browser_controller.py`** - Web automation
   - YouTube video search
   - Google search
   - Website navigation

4. **`app_automator.py`** - Messaging & productivity
   - WhatsApp messages
   - Email search

5. **`app_navigator.py`** - Main router
   - Natural language parsing
   - Routes to appropriate controller

## Setup

### 1. Grant Accessibility Permissions

```bash
System Preferences → Security & Privacy → Privacy → Accessibility
```

Add your Python executable or IDE (VS Code, PyCharm, Terminal).

### 2. Verify Installation

```python
from src.integrations.element_finder import AccessibilityHelper
print(AccessibilityHelper.get_frontmost_app())
```

## Supported Commands

### Spotify

| Command | Action |
|---------|--------|
| "play lo-fi beats on spotify" | Search and play song |
| "pause spotify" | Pause playback |
| "resume" / "continue" | Resume playback |
| "next song" / "skip" | Next track |
| "previous song" | Previous track |
| "what's playing" | Get current track |

### YouTube

| Command | Action |
|---------|--------|
| "search python tutorial on youtube" | Search and play video |
| "find dsa videos" | Search videos |
| "youtube binary search" | Search specific topic |

### Google Search

| Command | Action |
|---------|--------|
| "search how to reverse linked list" | Google search |
| "google dsa algorithms" | Search query |
| "look up graph traversal" | Search topic |

### WhatsApp

| Command | Action |
|---------|--------|
| "message john saying hey" | Send message |
| "whatsapp mom saying coming home" | Send message |

### Email

| Command | Action |
|---------|--------|
| "search emails for project" | Search Mail.app |
| "find emails from professor" | Search emails |

### Websites

| Command | Action |
|---------|--------|
| "open website github.com" | Navigate to site |
| "visit leetcode.com" | Open website |

## How It Works

### Example: "play lo-fi beats on spotify"

```
1. AppNavigator detects "spotify" + "play"
2. Extracts query: "lo-fi beats"
3. Routes to SpotifyController.search_and_play()
4. Opens Spotify app
5. Presses Cmd+K (search)
6. Types "lo-fi beats"
7. Presses Enter (search)
8. Presses Down Arrow + Enter (select first result)
9. Returns: "As you wish, sir. Now playing lo-fi beats on Spotify."
```

## Testing

### Test Individual Components

```python
# Test Spotify
from src.integrations.spotify_controller import SpotifyController
from src.core.mac_control import MacController

mac = MacController()
spotify = SpotifyController(mac)
spotify.search_and_play("lo-fi beats")

# Test Browser
from src.integrations.browser_controller import BrowserController
browser = BrowserController(mac)
browser.search_youtube("python tutorial")

# Test Full Integration
from src.core.agent import Jarvis
jarvis = Jarvis()
is_cmd, resp = jarvis.app_navigator.handle_app_navigation("play lo-fi beats on spotify")
print(resp)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Grant Accessibility permissions + restart IDE |
| Commands execute but nothing happens | Increase `time.sleep()` values |
| Spotify doesn't open | Verify Spotify installed |
| YouTube search fails | Check Chrome/Safari is default browser |
| Text typing scrambles | Reduce delay in `type_text()` |
| App not found | Use exact app name from Applications |

### Timing Adjustments

If commands fail, increase sleep times in controller files:

```python
# In spotify_controller.py
time.sleep(0.5)  # Increase to 1.0 if needed
```

## Extending the System

### Add New App Support

1. Create controller in `src/integrations/[app]_controller.py`
2. Add detection logic in `app_navigator.py`
3. Add handler method `_handle_[app]()`

Example:

```python
# In app_navigator.py
def _handle_new_app(self, user_input: str) -> Tuple[bool, str]:
    # Parse command
    # Call controller
    # Return response
    pass
```

## Technical Notes

- **No external dependencies** - Uses Python stdlib only
- **Timing sensitive** - Adjust delays for your Mac's speed
- **Keyboard shortcuts** - More reliable than UI clicking
- **AppleScript** - Native macOS automation
- **Error handling** - Graceful failures with user feedback

## Security

- All automation runs locally
- No external API calls (except GitHub if configured)
- Accessibility permissions required
- No data sent externally

## Performance

- Commands typically complete in 2-5 seconds
- App launch time is the main bottleneck
- Keyboard simulation is near-instant
- Network-dependent for web searches
