# 🛡️ SurakshaVaani — AI Safety Story Narrator

An AI-powered safety narration system for thermal power plants. Enter a safety rule → get a realistic Hindi story → narrated as audio with background music.

**Full offline pipeline — no cloud, no API keys.**

Built with **Mistral (Ollama) + Facebook NLLB-200 + Piper TTS + FFmpeg + FastAPI**.

---

## 🎯 What It Does

```
You type a safety rule (English)
        ↓
Mistral AI generates a realistic workplace incident story
        ↓
Facebook NLLB-200 translates it to Hindi
        ↓
Piper TTS narrates it in a Hindi voice
        ↓
FFmpeg mixes narration with mood-based background music
        ↓
You get an audio .wav file + story text in the browser
```

---

## ✨ Features

- 🤖 Unique story every time — random character, department, incident
- 🌐 Hindi translation via NLLB-200 (fully offline)
- 🎙️ Natural Hindi voice via Piper TTS
- 🎵 Auto mood detection — calm / tense / inspirational background music
- 🖥️ Clean industrial web UI
- 🔒 100% local — nothing sent to cloud

---

## 🏗️ Project Structure

```
suraksha-vaani/
├── backend/
│   ├── pipeline.py       # Core pipeline: story → translate → audio
│   └── server.py         # FastAPI server
├── frontend/
│   └── index.html        # Web UI
├── outputs/              # Generated .wav files (auto-created)
├── models/               # NLLB model folder (you download this)
├── piper/                # Piper TTS binary + voice model
│   ├── piper.exe
│   ├── espeak-ng-data/   # Required! Comes with Piper zip
│   └── models/
│       ├── hi_IN-pratham-medium.onnx
│       └── hi_IN-pratham-medium.onnx.json
├── ffmpeg/
│   └── bin/
│       └── ffmpeg.exe
├── music/
│   ├── calm.mp3
│   ├── tense.mp3
│   └── inspirational.mp3
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Setup — Step by Step

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/suraksha-vaani.git
cd suraksha-vaani
```

---

### Step 2 — Install Python dependencies

> ⚠️ **Use Python 3.11** — Python 3.13 has compatibility issues with several packages (sentencepiece, pydantic-core). Python 3.11 works without any compilation errors.
> Download Python 3.11: https://www.python.org/downloads/release/python-3119/

```bash
pip install -r requirements.txt
```

**Known install errors and fixes:**

**Error: `sentencepiece` fails to build**
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
ERROR: Failed to build sentencepiece
```
Fix:
```bash
pip install sentencepiece --only-binary=:all:
```
If that also fails, install Visual C++ Build Tools from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/
Check "Desktop development with C++" during install, then retry.

**Error: `torch==2.3.0` not found**
```
ERROR: Could not find a version that satisfies the requirement torch==2.3.0
```
Fix — edit `requirements.txt` and change to:
```
torch>=2.6.0
```

**Error: `pydantic-core==2.18.2` not found**
```
ERROR: Could not find a version that satisfies the requirement pydantic-core==2.18.2
```
Safely ignore this — pydantic installs correctly with a newer compatible version automatically.

---

### Step 3 — Install Ollama and pull Mistral

1. Download and install Ollama from: https://ollama.ai
2. Pull the Mistral model:
```bash
ollama pull mistral
```
3. Verify it works:
```bash
ollama run mistral "say hello"
```

> ⚠️ **Corporate network / proxy users:** Ollama calls from Python will fail with `ProxyError` or return empty output even though `ollama run` works fine in terminal.
>
> Fix — add these 2 lines at the very top of `backend/pipeline.py` (before all other code):
> ```python
> import os
> os.environ["NO_PROXY"] = "localhost,127.0.0.1"
> os.environ["no_proxy"] = "localhost,127.0.0.1"
> ```

> ⚠️ **Ollama not found from Python:** Even if `ollama` works in terminal, Python subprocess may not find it. Use the full path in your `.env`:
> ```
> OLLAMA_EXE=C:\Users\YOUR_USERNAME\AppData\Local\Programs\Ollama\ollama.exe
> ```
> Find your path with: `where ollama`

---

### Step 4 — Download NLLB Translation Model

```bash
pip install huggingface_hub
huggingface-cli download facebook/nllb-200-distilled-600M --local-dir ./models/nllb-200-distilled-600M
```

This downloads ~2.4GB. After download, `models/nllb-200-distilled-600M/` folder should exist.

---

### Step 5 — Download Piper TTS

1. Go to: https://github.com/rhasspy/piper/releases
2. Download `piper_windows_amd64.zip`
3. Extract it — you get a folder with `piper.exe` and `espeak-ng-data/` folder inside
4. Place contents so structure looks like:
```
piper/
├── piper.exe
├── espeak-ng-data/     ← DO NOT delete — Piper silently fails without this
└── models/
```

5. Download Hindi voice model from:
```
https://huggingface.co/rhasspy/piper-voices/tree/main/hi/IN/pratham/medium
```
Download **both** of these files:
- `hi_IN-pratham-medium.onnx`
- `hi_IN-pratham-medium.onnx.json`  ← ⚠️ Required. Without it Piper runs but produces no audio.

Place both files in `piper/models/`.

**Test Piper works before continuing:**
```bash
echo "Hello this is a test" | piper\piper.exe -m piper\models\hi_IN-pratham-medium.onnx -f test.wav
```
You should see `Real-time factor: ...` and a `test.wav` file gets created.

---

### Step 6 — Download FFmpeg

1. Go to: https://www.gyan.dev/ffmpeg/builds/
2. Download `ffmpeg-release-essentials.zip`
3. Extract — inside find the `bin/` folder containing `ffmpeg.exe`
4. Place at:
```
ffmpeg/
└── bin/
    └── ffmpeg.exe
```

---

### Step 7 — Add Background Music

Place 3 mp3 files in the `music/` folder. Get free music from https://pixabay.com/music/

| Filename | Search term on Pixabay |
|----------|----------------------|
| `calm.mp3` | ambient calm |
| `tense.mp3` | dramatic tense |
| `inspirational.mp3` | motivational uplifting |

---

### Step 8 — Configure Environment

```bash
copy .env.example .env
```

Edit `.env` with your actual paths:
```
NLLB_MODEL_PATH=./models/nllb-200-distilled-600M
OLLAMA_EXE=C:\Users\YOUR_USERNAME\AppData\Local\Programs\Ollama\ollama.exe
OLLAMA_MODEL=mistral
PIPER_EXE=./piper/piper.exe
PIPER_MODEL=./piper/models/hi_IN-pratham-medium.onnx
FFMPEG_EXE=./ffmpeg/bin/ffmpeg.exe
PLANT_NAME=YourPlantName
```

---

### Step 9 — Test pipeline from command line first

Always test the pipeline directly before running the server:
```bash
python backend/pipeline.py "Always wear PPE before entering operational areas"
```

This takes ~2-3 minutes. Expected output:
```json
{"story_en": "During a routine...", "story_hi": "पावर प्लांट में...", "audio_file": "outputs/xxxx.wav"}
```

Check that a `.wav` file appears in the `outputs/` folder.

---

### Step 10 — Run the server

```bash
python backend/server.py
```

Open browser at:
```
http://localhost:8000
```

> ⚠️ Do NOT open `index.html` directly from File Explorer. Always use `http://localhost:8000` — browsers block requests from `file://` to `http://`.

---

## 🐛 All Known Issues & Fixes

### 1. Proxy error on corporate network
```
ProxyError: Unable to connect to proxy
ConnectionResetError: [WinError 10054]
```
**Cause:** Company proxy intercepts localhost connections.
**Fix:** Add at very top of `backend/pipeline.py`:
```python
import os
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"
```

---

### 2. `lang_code_to_id` AttributeError
```
AttributeError: NllbTokenizerFast has no attribute lang_code_to_id
```
**Cause:** Newer `transformers` versions removed this attribute.
**Fix:** In `translate_en_to_hi` function:
```python
# Remove:
forced_bos_token_id = tokenizer.lang_code_to_id[tgt_lang]
# Replace with:
forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_lang)
```

---

### 3. Piper runs but no audio file created
```
RuntimeError: Piper ran but did not create audio file
```
**Cause 1:** Missing `hi_IN-pratham-medium.onnx.json` file.
**Fix:** Download the `.json` file from HuggingFace alongside the `.onnx` file.

**Cause 2:** `espeak-ng-data/` folder missing.
**Fix:** Re-extract Piper zip keeping all contents including `espeak-ng-data/`.

**Cause 3:** Text passed to Piper is empty because translation failed upstream.
**Fix:** Fix the translation issue first, then audio will work.

---

### 4. Ollama returns empty story (story length: 0)
```
DEBUG story length: 0
```
**Cause:** Python subprocess cannot find ollama or proxy is blocking it.
**Fix:** Use full absolute path in `.env`:
```
OLLAMA_EXE=C:\Users\YOUR_USERNAME\AppData\Local\Programs\Ollama\ollama.exe
```

---

### 5. FFmpeg cannot find music file
```
Error opening input file ...\backend\music\inspirational.mp3
```
**Cause:** Paths resolve to `backend/music/` instead of root `music/`.
**Fix:** In `pipeline.py`:
```python
# Change:
MUSIC_DIR  = os.path.join(BASE_DIR, "music")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
# To:
MUSIC_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
```

---

### 6. Windows asyncio NotImplementedError
```
raise NotImplementedError
NotImplementedError
```
**Cause:** `asyncio.create_subprocess_exec` does not work on Windows by default.
**Fix:** Add at top of `server.py`:
```python
import sys, asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```
And replace async subprocess with `ThreadPoolExecutor` + `subprocess.run`.

---

### 7. Frontend shows "Failed to fetch"
**Cause:** Opened `index.html` directly from File Explorer (`file:///...`).
**Fix:** Always use the server URL:
```
http://localhost:8000
```

---

### 8. Story text has strange characters (`\u001b[9D\u001b[K`)
**Cause:** Ollama outputs terminal cursor control escape codes.
**Fix:** Add to `generate_story` before return:
```python
story = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', story)
```

---

## ⚙️ Configuration (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `PLANT_NAME` | Plant name used in stories | `MyPlant Unit-2` |
| `OLLAMA_EXE` | Full path to ollama.exe | `C:\...\ollama.exe` |
| `OLLAMA_MODEL` | LLM model name | `mistral` |
| `NLLB_MODEL_PATH` | Path to NLLB model folder | `./models/nllb-200-distilled-600M` |
| `PIPER_EXE` | Path to Piper binary | `./piper/piper.exe` |
| `PIPER_MODEL` | Path to Hindi voice model | `./piper/models/hi_IN-pratham-medium.onnx` |
| `FFMPEG_EXE` | Path to FFmpeg binary | `./ffmpeg/bin/ffmpeg.exe` |

---

## 🧠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Story Generation | Mistral 7B via Ollama (local) |
| Hindi Translation | Facebook NLLB-200-distilled-600M |
| Text-to-Speech | Piper TTS — hi_IN-pratham-medium |
| Audio Mixing | FFmpeg |
| Backend API | FastAPI + Uvicorn |
| Frontend | HTML / CSS / JS |

---

## 📌 System Requirements

- Windows 10/11 (Linux works with path adjustments)
- Python 3.11 recommended (3.13 has package compatibility issues)
- 8GB+ RAM (NLLB ~4GB + Mistral ~4GB)
- GPU optional — CPU works but story generation takes ~2 minutes
- ~5GB disk space for models

---

**Nandini Jampana** — nandinijampana528@gmail.com  
[GitHub](https://github.com/nandinijampana528/) · [LinkedIn](https://www.linkedin.com/in/nandini-jampana-714524172/)

---

## 📄 License

MIT
