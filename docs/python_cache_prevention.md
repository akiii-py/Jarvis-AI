# Python Cache Prevention Guide

## What is Python Cache?

Python automatically creates bytecode cache files (`.pyc`) in `__pycache__/` directories to speed up module loading. While this improves performance, it can cause issues during development when code changes aren't reflected.

## Prevention Measures Implemented

### 1. `.gitignore` Updated
- Prevents cache files from being committed to git
- Ensures clean repository

### 2. `jarvis.sh` Auto-Clears Cache
The launcher script now automatically clears cache before starting:
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 3. Manual Cache Clearing

If you ever need to manually clear cache:

```bash
# Clear all cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Or use Python
python -Bc "import compileall; compileall.compile_dir('.', force=True)"
```

## Best Practices

### During Development:

1. **Use the launcher script:**
   ```bash
   jarvis  # Automatically clears cache
   ```

2. **Or run with Python's `-B` flag:**
   ```bash
   python -B main.py  # Don't write .pyc files
   ```

3. **Set environment variable:**
   ```bash
   export PYTHONDONTWRITEBYTECODE=1
   python main.py
   ```

### When to Clear Cache Manually:

- After pulling new code from git
- After editing core modules (llm.py, agent.py, personality.py)
- When seeing unexpected behavior
- Before testing new features

## Why Cache Exists

**Benefits:**
- Faster startup time (no recompilation)
- Reduced CPU usage
- Better performance in production

**Drawbacks:**
- Can serve stale code during development
- Takes up disk space
- Can cause confusion

## Solution Summary

✅ **Automatic:** `jarvis.sh` clears cache on every start
✅ **Git:** `.gitignore` prevents cache from being committed  
✅ **Manual:** Easy commands to clear when needed

**You should never have this issue again!** 🎯
