# Quick Start Guide

## Running JARVIS

### Option 1: Using the Launcher Script (Recommended) ✨

Run JARVIS from **anywhere** with a single command:

```bash
# From any directory
/Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh
```

Or create an alias for even easier access:

```bash
# Add to your ~/.zshrc or ~/.bash_profile
echo 'alias jarvis="/Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh"' >> ~/.zshrc
source ~/.zshrc

# Now you can run JARVIS from anywhere with just:
jarvis
```

### Option 2: Manual Launch

```bash
cd /Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity
./venv/bin/python main.py
```

---

## What the Launcher Does

The `jarvis.sh` script automatically:
- ✅ Finds the correct project directory
- ✅ Activates the virtual environment
- ✅ Checks for required files
- ✅ Displays a nice startup banner
- ✅ Handles all path issues

---

## Creating a Global Command

To run JARVIS with just `jarvis` from anywhere:

### Step 1: Create an alias

```bash
# For zsh (default on macOS)
echo 'alias jarvis="/Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'alias jarvis="/Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh"' >> ~/.bash_profile
source ~/.bash_profile
```

### Step 2: Test it

```bash
# From any directory
jarvis
```

---

## Alternative: Symlink to /usr/local/bin

For system-wide access:

```bash
sudo ln -s /Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh /usr/local/bin/jarvis

# Now run from anywhere
jarvis
```

---

## Troubleshooting

### "Permission denied" error
```bash
chmod +x /Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh
```

### "Virtual environment not found"
```bash
cd /Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity
python3 -m venv venv
pip install -r requirements.txt
```

### Script doesn't work
Make sure you're using the full path:
```bash
/Users/akshat/Desktop/Projects/Jarvis_AI_Antigravity/jarvis.sh
```

---

## Quick Commands After Launch

Once JARVIS starts, try:
- "play lo-fi beats on spotify"
- "search python tutorial on youtube"
- "set volume to 50"
- "focus mode for 2 hours"
- "prepare for coding"

Enjoy! 🚀
