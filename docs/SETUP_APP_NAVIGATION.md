# Quick Setup Guide - App Navigation

## Step 1: Grant Accessibility Permissions ⚠️ REQUIRED

The app navigation system needs macOS Accessibility permissions to control applications.

### How to Grant Permissions:

1. **Open System Preferences**
   ```
   System Preferences → Security & Privacy → Privacy → Accessibility
   ```

2. **Click the lock icon** (bottom left) to make changes

3. **Add one of these** (depending on how you run JARVIS):

   **Option A: If running from Terminal**
   - Click the `+` button
   - Navigate to `/Applications/Utilities/Terminal.app`
   - Select and add it
   
   **Option B: If running from VS Code**
   - Click the `+` button
   - Navigate to `/Applications/Visual Studio Code.app`
   - Select and add it
   
   **Option C: If running from PyCharm**
   - Click the `+` button
   - Navigate to `/Applications/PyCharm.app`
   - Select and add it

4. **Restart JARVIS** after granting permissions

### Verify Permissions

Run this test to verify:

```python
from src.integrations.element_finder import AccessibilityHelper

# Should print the name of your active app
print(AccessibilityHelper.get_frontmost_app())
```

If it prints the app name, you're good to go! ✅

---

## Step 2: Test Commands

Try these commands to test the system:

### Spotify (requires Spotify app installed)
```
"play lo-fi beats on spotify"
"pause spotify"
"next song"
```

### YouTube
```
"search python tutorial on youtube"
"youtube binary search"
```

### Google
```
"search dsa algorithms"
"google linked list reversal"
```

### WhatsApp (requires WhatsApp desktop app)
```
"message john saying hey"
```

### Email
```
"search emails for project"
```

---

## Troubleshooting

### Commands don't work
- **Check permissions**: Make sure Terminal/IDE is in Accessibility list
- **Restart JARVIS**: Permissions need app restart to take effect
- **Check app is installed**: Spotify, WhatsApp, etc. must be installed

### Commands are slow
- **Increase delays**: Edit controller files and increase `time.sleep()` values
- **Example**: In `spotify_controller.py`, change `time.sleep(0.5)` to `time.sleep(1.0)`

### Typing scrambles
- **Reduce typing speed**: In `element_finder.py`, change `delay=0.05` to `delay=0.03`

### App doesn't open
- **Check app name**: Use exact name from Applications folder
- **Try manually**: Open app first, then try control commands

---

## What Works Now

✅ **Spotify**: Full control (search, play, pause, next/previous)  
✅ **YouTube**: Search and play videos  
✅ **Google**: Web searches  
✅ **WhatsApp**: Send messages  
✅ **Email**: Search Mail.app  
✅ **Websites**: Navigate to any URL  

---

## Next Steps

Once this works, you can:
1. Add more apps (Calendar, Notes, etc.)
2. Customize timing for your Mac's speed
3. Add more complex workflows
4. Integrate with existing focus mode and scheduling

---

**Need help?** Check `docs/APP_NAVIGATION_GUIDE.md` for full documentation.
