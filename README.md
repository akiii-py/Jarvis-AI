# JARVIS AI Agent 🤖

A movie-accurate recreation of Tony Stark's JARVIS AI assistant from the Marvel Cinematic Universe. Built with Python, Ollama, and local-first AI models.

## ✨ Features

### 🎭 Movie-Accurate Personality
- Sophisticated British formality with dry wit and sarcasm
- Context-aware responses (time of day, session duration, user state)
- Escalating concern system for user wellbeing
- Genuine loyalty wrapped in understated humor

### 🧠 Intelligence
- **Dynamic Model Switching**: Switch between specialized models
  - `coding` mode: qwen2.5-coder (programming, debugging, DSA)
  - `research` mode: deepseek-r1 (deep reasoning, analysis)
  - `general` mode: mistral:7b (conversation)
- **Persistent Memory**: Remembers conversations across sessions
- **User-Controlled Memory**: "Remember this" / "Forget that" commands
- **Name Learning**: Learns and remembers your name
- **Context-Aware Responses**: Adapts personality based on time, mode, and session duration

### 🎤 Voice Interface
- **Wake Word Detection**: "Jarvis" activation (Porcupine)
- **Free Alternative**: Energy-based voice detection (no API key needed)
- **Speech-to-Text**: Whisper (local, private)
- **Text-to-Speech**: macOS `say` command

### 🖥️ Mac Control
- **App Launcher**: Open/close applications with natural language
  - "launch mail", "open chrome", "close discord"
  - Smart app name recognition (email→Mail, vscode→VS Code)
- **System Controls**: Volume and brightness adjustment
  - "set volume to 50", "volume up", "mute"
  - "brightness up", "set brightness to 75"
- **Command Chaining**: Execute multiple commands at once
  - "open chrome and launch mail"

### 🎯 Productivity Features
- **Smart Focus Mode**: Block distractions during work sessions
  - "focus mode for 2 hours" - Blocks non-work apps
  - Tracks interruptions and provides end-of-session summary
- **Workflow Chains**: Automated multi-step tasks
  - "prepare for coding" - Opens VS Code, Terminal, Chrome, sets volume
  - "prepare for research" - Opens research apps, switches mode
  - "end session" - Closes work apps, opens Mail
- **Persistent Settings**: Remembers your preferences
  - Default volume, brightness, and mode
  - Auto-applied on startup
- **Scheduling & Reminders**: Time-based automation
  - "remind me in 30 minutes" - One-time reminders
  - "every day at 9 AM open mail" - Recurring tasks
  - Automated task execution
- **Command Logging**: Track all commands with analytics
  - "show command history" - View recent commands

### 🐙 GitHub Integration
- **Repository Management**: Control GitHub from voice/text
  - "show my repos" - List repositories
  - "create repo my-project" - Create new repo
  - "latest commit" - View recent commit
- **Git Operations**: Local git automation
  - "git status" - Check repo status
  - "git push" / "git pull" - Sync with remote
  - "commit and push with message [msg]" - Quick workflow
  - "list branches" - Show all branches

### 🔧 Current Capabilities
- Natural conversation with context awareness
- Code assistance and explanations
- Model switching for different tasks
- Session monitoring with fatigue warnings
- Mac system control and automation
- Productivity workflows and focus sessions

## 🚀 Quick Start

### Prerequisites
- macOS (for TTS)
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running

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

**Quick Launch (Recommended)**
```bash
./jarvis.sh
```

**Text Mode**
```bash
python main.py
```

**Voice Mode (Free - No API Key)**
```bash
python main.py --voice
```

**Voice Mode with Porcupine (Optional)**
```bash
export PICOVOICE_ACCESS_KEY="your-key-here"
python main.py --voice
```

## 🎮 Commands

### Core Commands
| Command | Description |
|---------|-------------|
| `switch to coding mode` | Use qwen2.5-coder for programming |
| `switch to research mode` | Use deepseek-r1 for deep reasoning |
| `switch to general mode` | Use mistral for conversation |
| `what mode` | Check current model |
| `my name is [name]` | Teach JARVIS your name |
| `remember [fact]` | Save important information |
| `forget that` | Clear custom memories |
| `clear history` | Wipe conversation history |
| `exit` / `quit` | Exit JARVIS |

### Mac Control
| Command | Description |
|---------|-------------|
| `open [app]` / `launch [app]` | Open an application |
| `close [app]` / `quit [app]` | Close an application |
| `open [app] and launch [app]` | Open multiple apps |
| `set volume to [0-100]` | Set system volume |
| `volume up` / `volume down` | Adjust volume |
| `mute` / `max volume` | Quick volume presets |
| `set brightness to [0-100]` | Set display brightness |
| `brightness up` / `brightness down` | Adjust brightness |

### Productivity
| Command | Description |
|---------|-------------|
| `focus mode for [X] hours/minutes` | Start focus session |
| `end focus` / `stop focus` | End focus session |
| `focus status` | Check remaining focus time |
| `prepare for coding` | Run coding workflow |
| `prepare for research` | Run research workflow |
| `end session` | Run end session workflow |
| `list workflows` | Show available workflows |

### Settings & Analytics
| Command | Description |
|---------|-------------|
| `set my default volume to [X]` | Save volume preference |
| `set my default mode to [mode]` | Save mode preference |
| `show my settings` | Display saved preferences |
| `show command history` | View recent commands |

### Scheduling & Reminders
| Command | Description |
|---------|-------------|
| `remind me in [X] minutes/hours` | Set one-time reminder |
| `remind me in [X] minutes to [message]` | Reminder with custom message |
| `every day at [time] open [app]` | Daily recurring task |
| `list scheduled` / `my reminders` | Show all scheduled tasks |
| `cancel reminder` / `cancel task` | Cancel most recent task |

### GitHub & Git
| Command | Description |
|---------|-------------|
| `show my repos` / `list my repos` | List your GitHub repositories |
| `create repo [name]` | Create new GitHub repository |
| `latest commit` / `last commit` | Show most recent commit |
| `git status` / `repo status` | Check repository status |
| `git push` / `push changes` | Push to remote |
| `git pull` / `pull changes` | Pull from remote |
| `commit and push` | Quick add, commit, and push |
| `commit and push with message [msg]` | Custom commit message |
| `list branches` / `show branches` | Show all branches |

## 📁 Project Structure

```
Jarvis_AI_Antigravity/
├── src/
│   ├── core/
│   │   ├── agent.py          # Main agent logic
│   │   ├── llm.py             # Ollama client
│   │   ├── memory.py          # Conversation & preferences
│   │   ├── personality.py     # JARVIS personality system
│   │   ├── mac_control.py     # macOS system control
│   │   ├── focus_mode.py      # Focus mode system
│   │   ├── workflows.py       # Workflow executor
│   │   ├── voice_io.py        # STT/TTS
│   │   ├── wake_word.py       # Porcupine integration
│   │   └── simple_wake.py     # Free wake detection
│   ├── config/
│   │   └── config.py          # Configuration
│   └── main.py                # Entry point
├── tests/
│   ├── test_model_switching.py
│   ├── test_mac_control.py
│   └── test_close_app.py
├── data/                      # Persistent storage (gitignored)
│   ├── conversation_history.json
│   ├── preferences.json
│   └── command_history.json
├── jarvis.sh                  # Quick launch script
├── activate.sh                # Venv activation helper
├── requirements.txt
└── README.md
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

This is a personal project, but suggestions and feedback are welcome! Feel free to open issues or submit pull requests.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by JARVIS from the Marvel Cinematic Universe
- Built with [Ollama](https://ollama.ai/)
- Powered by open-source LLMs (Qwen, DeepSeek, Mistral)
- Voice detection by [Picovoice Porcupine](https://picovoice.ai/)
- Speech recognition by [OpenAI Whisper](https://github.com/openai/whisper)

## ⚠️ Disclaimer

This project is a fan recreation and is not affiliated with Marvel, Disney, or any related entities. JARVIS is a trademark of Marvel Entertainment.

---

**"At your service, sir."** - JARVIS
