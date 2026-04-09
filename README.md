# 🛡️ SurakshaVaani — AI Safety Story Narrator

An AI-powered safety narration system for **thermal power plants**. Enter a safety rule → get a realistic story about it → translated to Hindi → narrated as audio with background music.

Built with **Mistral (Ollama) + NLLB-200 (Facebook) + Piper TTS + FFmpeg**.

---

## 🎯 What It Does

```
Safety Rule (English)
       ↓
  Mistral AI generates a realistic workplace incident story
       ↓
  NLLB-200 translates to Hindi
       ↓
  Piper TTS narrates in Hindi voice
       ↓
  FFmpeg mixes with background music (calm / tense / inspirational)
       ↓
  Audio .wav file ready for playback
```

---

## ✨ Features

- 🤖 **AI Story Generation** — Mistral creates unique, realistic incident stories every time
- 🌐 **Hindi Translation** — Facebook NLLB-200 model (runs fully offline)
- 🎙️ **Hindi Voice Narration** — Piper TTS with natural-sounding voice
- 🎵 **Mood-based Music** — auto-detects tone (tense/calm/inspirational) and mixes background music
- 🖥️ **Web UI** — clean industrial-themed frontend
- 🔒 **Fully Offline** — no data sent to cloud (except Ollama local model)

---

## 🏗️ Project Structure

```
suraksha-vaani/
├── backend/
│   ├── pipeline.py      # Core: story → translate → audio
│   └── server.py        # FastAPI server
├── frontend/
│   └── index.html       # Web UI
├── outputs/             # Generated .wav files (git-ignored)
├── models/              # NLLB model (git-ignored, download separately)
├── piper/               # Piper TTS binary + models (git-ignored)
├── ffmpeg/              # FFmpeg binary (git-ignored)
├── music/               # Background music files (git-ignored)
│   ├── calm.mp3
│   ├── tense.mp3
│   └── inspirational.mp3
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/suraksha-vaani.git
cd suraksha-vaani
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install & start Ollama, pull Mistral
```bash
# Install Ollama: https://ollama.ai
ollama pull mistral
```

### 4. Download NLLB model
```bash
# Using HuggingFace CLI
pip install huggingface_hub
huggingface-cli download facebook/nllb-200-distilled-600M --local-dir ./models/nllb-200-distilled-600M
```

### 5. Download Piper TTS
- Download from: https://github.com/rhasspy/piper/releases
- Place binary at `piper/piper.exe` (Windows) or `piper/piper` (Linux)
- Download Hindi voice model: `hi_IN-pratham-medium.onnx`
- Place at `piper/models/hi_IN-pratham-medium.onnx`

### 6. Download FFmpeg
- Download from: https://ffmpeg.org/download.html
- Place at `ffmpeg/bin/ffmpeg.exe`

### 7. Add background music
Place 3 mp3 files in `music/` folder:
- `calm.mp3`
- `tense.mp3`
- `inspirational.mp3`

### 8. Configure environment
```bash
cp .env.example .env
# Edit .env — set PLANT_NAME and paths as needed
```

### 9. Run the server
```bash
python backend/server.py
```

Open `http://localhost:8000` in your browser.

---

## 🎮 Usage

1. Enter your **plant name** (optional)
2. Type or select a **safety rule**
3. Click **Generate Safety Story**
4. Wait ~60–90 seconds for full pipeline
5. Read story in English + Hindi
6. Play or download the Hindi audio narration

---

## ⚙️ Configuration

All settings in `.env`:

| Variable | Description |
|----------|-------------|
| `PLANT_NAME` | Plant name used in stories |
| `OLLAMA_MODEL` | LLM model (default: mistral) |
| `NLLB_MODEL_PATH` | Path to NLLB model folder |
| `PIPER_EXE` | Path to Piper binary |
| `PIPER_MODEL` | Path to Hindi voice model |
| `FFMPEG_EXE` | Path to FFmpeg binary |

---

## 🧠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Story Generation | Mistral 7B via Ollama |
| Translation | Facebook NLLB-200-distilled-600M |
| TTS | Piper TTS (hi_IN-pratham-medium) |
| Audio Mixing | FFmpeg |
| Backend API | FastAPI |
| Frontend | HTML/CSS/JS |

---

## 📌 Requirements

- Python 3.10+
- Windows / Linux
- Ollama installed
- 4GB+ RAM (for NLLB model)
- GPU optional (CPU works, slower)

---

## 📄 License

MIT
