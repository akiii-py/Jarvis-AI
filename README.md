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

### 🎤 Voice Interface
- **Wake Word Detection**: "Jarvis" activation (Porcupine)
- **Free Alternative**: Energy-based voice detection (no API key needed)
- **Speech-to-Text**: Whisper (local, private)
- **Text-to-Speech**: macOS `say` command

### 🔧 Current Capabilities
- Natural conversation with context awareness
- Code assistance and explanations
- Model switching for different tasks
- Session monitoring with fatigue warnings
- Persistent preferences and memory

## 🚀 Quick Start

### Prerequisites
- macOS (for TTS)
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/Jarvis_AI_Antigravity.git
cd Jarvis_AI_Antigravity
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

**Text Mode (Recommended for first run)**
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

## 📁 Project Structure

```
Jarvis_AI_Antigravity/
├── src/
│   ├── core/
│   │   ├── agent.py          # Main agent logic
│   │   ├── llm.py             # Ollama client
│   │   ├── memory.py          # Conversation & preferences
│   │   ├── personality.py     # JARVIS personality system
│   │   ├── voice_io.py        # STT/TTS
│   │   ├── wake_word.py       # Porcupine integration
│   │   └── simple_wake.py     # Free wake detection
│   ├── config/
│   │   └── config.py          # Configuration
│   └── main.py                # Entry point
├── tests/
│   └── test_model_switching.py
├── data/                      # Persistent storage (gitignored)
├── requirements.txt
└── README.md
```

## 🛣️ Roadmap

- [x] **Phase 1A**: Foundation (LLM, memory, config)
- [x] **Phase 1B**: Voice & Personality
- [ ] **Phase 1C**: Mac Control & Files
- [ ] **Phase 1D**: Coding Companion
- [ ] **Phase 1E**: Study Sidekick
- [ ] **Integration & Testing**

See [task.md](https://github.com/YOUR_USERNAME/Jarvis_AI_Antigravity/blob/main/.gemini/antigravity/brain/2ad6012e-2eac-4cce-bf00-38df593a0570/task.md) for detailed progress.

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
