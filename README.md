# JARVIS AI Agent 🤖

A movie-accurate recreation of Tony Stark's JARVIS AI assistant from the Marvel Cinematic Universe. Built with Python, Ollama, and local-first AI models.

## ✨ Features

### 🎭 Movie-Accurate Personality
- Sophisticated British formality with dry wit and sarcasm
- **Context-Aware Responses**: Logic changes based on time (tired at night), coding mode (technical), or long sessions (concerned)
- **Escalating Loyalty**: Genuine care for user wellbeing
- **Dynamic Interaction**: "Push-to-talk" and "Barge-in" interruption capability

### 🗣️ Advanced Voice System
- **Speech-to-Text**: Local Whisper model for accurate transcription
- **Text-to-Speech**: **ElevenLabs Integration** for premium, movie-like British voice
- **Wake Methods**:
  - **Keyboard Wake**: Press `Space` to talk, press again to stop (Unlimited duration)
  - **Picovoice**: "Hey Jarvis" wake word detection (Optional)

### 🧠 Intelligence & Features
- **Morning Briefing Protocol** ☀️: "Start my day"
  - Weather report (Real-time)
  - Tech news headlines
  - System status & Battery check
- **Research Agent** 🕵️‍♂️: "Research [topic]"
  - **Terminal-Only Mode**: Searches internet visibly in terminal, no browser window
  - **Deep Analysis**: Reads multiple sources and synthesizes a report
  - **Auto-Reports**: Saves markdown reports to `data/research_reports/`
- **Calendar Integration** 📅: "Schedule meeting..."
  - **Silent Operation**: Adds events in the background via AppleScript without opening the Calendar app
  - **Smart Date Parsing**: Robustly assumes future dates and handles cross-region locale differences (DD/MM vs MM/DD)
  - **Google Calendar Sync**: Prioritizes syncing with Google Calendar accounts
- **Dynamic Model Switching**:
  - `coding` mode: qwen2.5-coder (programming, debugging)
  - `research` mode: deepseek-r1 (deep reasoning)
  - `general` mode: mistral:7b (conversation)
- **App Navigation System** 🧭:
  - **Spotify**: Play songs, control playback ("Play Back in Black")
  - **Browser**: Search Google, open URLs, manage tabs
  - **YouTube**: Search and play videos directly
  - **System**: Volume, brightness, app launching/closing

### 🔧 Productivity
- **Smart Focus Mode**: Blocks distractions for set duration
- **GitHub Integration**: Manage repos, push/pull code via voice
- **Scheduling**: Reminders and recurring daily tasks
- **Calendar Integration**: Natural language event scheduling
- **Command Logging**: Tracks usage history

## 🚀 Quick Start

### Prerequisites
- macOS (Required for system control integration)
- Python 3.10+
- [Ollama](https://ollama.ai/) installed
- [ffmpeg](https://ffmpeg.org/) (for audio processing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/Jarvis-AI.git
cd Jarvis-AI
```

2. **Set up virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Ollama models**
```bash
ollama pull qwen2.5-coder:latest
ollama pull deepseek-r1:latest
ollama pull mistral:7b
```

5. **Start Ollama**
```bash
ollama serve
```

### Usage

**Launch JARVIS (Text Mode)**
```bash
python main.py
```

**Launch JARVIS (Voice Mode)** 🎙️
```bash
python main.py --voice
```
_Press SPACE/ENTER to start talking. Press again to stop._

## 🎮 Command Guide

### ☀️ Morning & Daily
| Command | Action |
|---------|--------|
| "Start my day" | Runs Morning Briefing Protocol |
| "Morning briefing" | Weather, News, System Status |
| "What's the update" | Quick status check |

### 🕵️‍♂️ Research Agent
| Command | Action |
|---------|--------|
| "Research [topic]" | Deep dive research (Terminal only) |
| "Search for [topic]" | Search web and summarize |
| "Find info on [topic]" | Gather info from multiple sources |
| "Latest [topic] news" | Get latest updates |

### 🧭 App Navigation
| Command | Action |
|---------|--------|
| "Open [App]" | Launch any application |
| "Close [App]" | Quit an application |
| "Google [X]" | Opens browser with search results |
| "Search YouTube for [X]" | Opens YouTube video directly |
| "Go to [website.com]" | Navigates to specific URL |

### 🎵 Media Control (Spotify)
| Command | Action |
|---------|--------|
| "Play [Song Name]" | Search and play song |
| "Play [Song] by [Artist]" | Specific track playback |
| "Pause" / "Resume" | Toggle playback |
| "Next track" | Skip song |
| "Volume [0-100]" | Set system volume |

### 💻 GitHub & Coding
| Command | Action |
|---------|--------|
| "Show my repos" | List GitHub repositories |
| "Create repo [name]" | Create new public repo |
| "Commit and push" | Stage, commit, and push |
| "Switch to coding mode" | Activate specialized coding model |

### 🧠 Memory & Utility
| Command | Action |
|---------|--------|
| "Remind me in [X] mins" | Set a timer/reminder |
| "Remember [fact]" | Store info in long-term memory |
| "Focus mode for [X] hours" | Block distractions |
| "Schedule meeting with [Person] [Time]" | Create calendar event |
| "Add event [Name] [Time]" | Add to macOS Calendar |

## 📁 Project Structure

```
Jarvis_AI_Antigravity/
├── src/
│   ├── core/
│   │   ├── agent.py          # Main brain & event loop
│   │   ├── personality_v2.py # Context-aware personality engine
│   │   ├── voice_io.py       # ElevenLabs TTS + Whisper STT
│   │   ├── keyboard_wake.py  # Push-to-talk system
│   │   └── mac_control.py    # System integration
│   ├── features/
│   │   ├── morning_briefing.py # Daily briefing logic
│   │   └── research_agent.py   # Web scraper & report generator
│   ├── integrations/
│   │   ├── app_navigator.py  # App control router
│   │   ├── browser_controller.py # Web automation
│   │   ├── calendar_controller.py # macOS Calendar automation
│   │   ├── spotify_controller.py # Spotify AppleScript control
│   │   ├── web_scraper.py    # Headless internet search
│   │   └── intent_detector.py # LLM-based intent parser
│   └── config/
└── main.py                   # Entry point
```

## 🛣️ Roadmap

- [x] **Phase 1A**: Foundation (LLM, memory, config)
- [x] **Phase 1B**: Voice & Personality
- [x] **Phase 1C**: Mac Control & Productivity Features
  - [x] App launcher and system controls
  - [x] Smart focus mode
  - [x] Workflow chains
  - [x] Command logging and analytics
- [ ] **Phase 1D**: Coding Companion
- [ ] **Phase 1E**: Study Sidekick
- [ ] **Integration & Testing**

See [task.md](https://github.com/akiii-py/Jarvis-AI/blob/main/.gemini/antigravity/brain/2ad6012e-2eac-4cce-bf00-38df593a0570/task.md) for detailed progress.

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

## 📄 License

MIT License.

## 🙏 Acknowledgments

- **Marvel Studios** for the inspiration
- **Ollama** for local LLM power
- **ElevenLabs** for the incredible voice
- **Picovoice & OpenAI** for audio tech

## ⚠️ Disclaimer

This project is a fan recreation and is not affiliated with Marvel, Disney, or any related entities. JARVIS is a trademark of Marvel Entertainment.

---

**"At your service, sir."** - JARVIS
