import subprocess
import random
import re
import torch
import sys
import json
import uuid
import os
import time

sys.stdout.reconfigure(encoding="utf-8")

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

start_time = time.time()

# =========================
# CONFIG — edit in .env or directly here
# =========================
NLLB_MODEL   = os.getenv("NLLB_MODEL_PATH", "./models/nllb-200-distilled-600M")
PIPER_EXE    = os.getenv("PIPER_EXE",   "./piper/piper.exe")
PIPER_MODEL  = os.getenv("PIPER_MODEL", "./piper/models/hi_IN-pratham-medium.onnx")
OLLAMA_EXE = os.getenv("OLLAMA_EXE", r"C:\Users\NSPCL\AppData\Local\Programs\Ollama\ollama.exe")          # just "ollama" if on PATH
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
FFMPEG_EXE   = os.getenv("FFMPEG_EXE",  "./ffmpeg/bin/ffmpeg.exe")
PLANT_NAME   = os.getenv("PLANT_NAME",  "PowerPlant")      # set to your plant name

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
MUSIC_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")

CALM_MUSIC  = os.path.join(MUSIC_DIR, "calm.mp3")
TENSE_MUSIC = os.path.join(MUSIC_DIR, "tense.mp3")
INSP_MUSIC  = os.path.join(MUSIC_DIR, "inspirational.mp3")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# LOAD NLLB TRANSLATION MODEL
# =========================
def debug(msg):
    print(f"[{time.time()-start_time:.1f}s] {msg}", file=sys.stderr)

debug("Loading NLLB translation model...")
tokenizer = AutoTokenizer.from_pretrained(NLLB_MODEL, local_files_only=True)
model     = AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL, local_files_only=True)
debug("NLLB model loaded.")


# =========================
# UTILITIES
# =========================
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return text.strip()

def clean_hindi(text):
    text = re.sub(r"\s+([।,!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def detect_mood(text):
    t = text.lower()
    if any(w in t for w in ["injury", "hospital", "burn", "shock", "serious", "accident"]):
        return "tense"
    elif any(w in t for w in ["near miss", "minor", "lesson", "realized", "avoided"]):
        return "calm"
    else:
        return "inspirational"


# =========================
# STORY GENERATION (OLLAMA / MISTRAL)
# =========================
def generate_story(rule: str, plant_name: str = PLANT_NAME) -> str:
    indian_names = [
        "Ramesh Kumar", "Suresh Yadav", "Vikram Singh",
        "Arun Mishra", "Deepak Sharma", "Mahesh Verma",
        "Rahul Tiwari", "Anil Gupta", "Sanjay Patel",
        "Prakash Nair", "Amit Kulkarni", "Manoj Joshi"
    ]
    departments = [
        "Coal Handling Plant", "Turbine Maintenance Section",
        "Boiler Platform", "Switchyard Area",
        "Ash Handling Unit", "Cooling Tower Section"
    ]
    job_roles = [
        "Senior Technician", "Maintenance Fitter",
        "Electrical Technician", "Shift Technician", "Mechanical Supervisor"
    ]
    unsafe_actions = [
        "skipped the Lockout-Tagout (LOTO) isolation procedure",
        "started work without verifying the Permit-To-Work (PTW)",
        "ignored proper barricading of the work zone",
        "removed his safety helmet for convenience",
        "failed to conduct a proper toolbox talk before beginning the task"
    ]
    incident_types = [
        "a sudden conveyor jerk", "an unexpected steam leakage",
        "a minor electrical arc flash",
        "a falling metallic tool from overhead maintenance",
        "a slip on oil-contaminated flooring"
    ]

    name     = random.choice(indian_names)
    dept     = random.choice(departments)
    role     = random.choice(job_roles)
    unsafe   = random.choice(unsafe_actions)
    incident = random.choice(incident_types)

    prompt = f"""You are a senior safety officer at {plant_name}, a thermal power plant.

Write a realistic safety incident story (200-230 words) focused on awareness, not fear.

MANDATORY:
- Plant: {plant_name}
- Character: Indian male named {name}, designation: {role}
- Location: {dept}
- Unsafe act: {unsafe}
- Incident: {incident}
- Describe: what job was done, root cause, what went wrong technically, supervisor reaction, corrective actions, reference to PPE/LOTO/PTW/toolbox talk

STYLE:
- Do NOT use dramatic or cinematic language
- Do NOT start with "In the heart of...", "Amidst the vast...", etc.
- Start like: "During a routine maintenance job...", "On a regular shift..."
- Tone: practical, calm, professional
- No exaggeration, no drama
- No title line
- End with a short professional safety message
- Story must feel different every time

Safety rule to base story on:
"{rule}"
"""

    result = subprocess.run(
        [OLLAMA_EXE, "run", OLLAMA_MODEL],
        input=prompt.encode("utf-8"),
        capture_output=True
    )
    story = result.stdout.decode("utf-8", errors="ignore")
    print(f"DEBUG story length: {len(story)}", file=sys.stderr)
    print(f"DEBUG story preview: {story[:200]}", file=sys.stderr)
    
    story = re.sub(r"^Title:.*?\n", "", story, flags=re.IGNORECASE)
    return clean_text(story)


# =========================
# TRANSLATION: English → Hindi (NLLB, sentence-chunked)
# =========================
def translate_en_to_hi(text: str) -> str:
    tokenizer.src_lang = "eng_Latn"
    tgt_lang = "hin_Deva"
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_lang)

    sentences = split_sentences(text)
    translated = []

    for sent in sentences:
        if not sent.strip():
            continue
        inputs = tokenizer(sent, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=256,
                num_beams=5
            )
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if result.strip():
            translated.append(clean_hindi(result))

    hindi_text = " ".join(translated)
    hindi_text = re.sub(r"^शीर्षक:.*?\n?", "", hindi_text, flags=re.IGNORECASE)
    hindi_text = clean_hindi(hindi_text)

    # DEBUG
    print(f"DEBUG hindi_text length: {len(hindi_text)}", file=sys.stderr)
    print(f"DEBUG hindi_text preview: {hindi_text[:200]}", file=sys.stderr)

    # Fallback to English if translation empty
    if not hindi_text.strip():
        print("WARNING: Hindi translation empty, using English text", file=sys.stderr)
        return text

    return hindi_text


# =========================
# AUDIO GENERATION (Piper TTS + FFmpeg music mix)
# =========================
def generate_audio(text: str, output_file: str):
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(backend_dir, "..")
    
    temp_voice = os.path.join(backend_dir, "temp_voice.wav")
    temp_text  = os.path.join(backend_dir, "temp_input.txt")

    print(f"DEBUG piper_exe: {PIPER_EXE}", file=sys.stderr)
    print(f"DEBUG piper_model: {PIPER_MODEL}", file=sys.stderr)
    print(f"DEBUG temp_voice: {temp_voice}", file=sys.stderr)
    print(f"DEBUG temp_text: {temp_text}", file=sys.stderr)
    print(f"DEBUG cwd: {project_dir}", file=sys.stderr)

    # Replace the Piper subprocess block with:
    with open(temp_text, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"DEBUG text to speak: {text[:100]}", file=sys.stderr)
    print(f"DEBUG text file written, size: {os.path.getsize(temp_text)}", file=sys.stderr)

    piper_result = subprocess.run(
        [PIPER_EXE, "-m", PIPER_MODEL, "-f", temp_voice],
        input=text.encode("utf-8"),
        capture_output=True,
        cwd=os.path.abspath(project_dir)
    )

    print(f"DEBUG piper returncode: {piper_result.returncode}", file=sys.stderr)
    print(f"DEBUG piper stdout: {piper_result.stdout.decode('utf-8', errors='ignore')}", file=sys.stderr)
    print(f"DEBUG piper stderr: {piper_result.stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
    print(f"DEBUG temp_voice exists: {os.path.exists(temp_voice)}", file=sys.stderr)

    if piper_result.returncode != 0:
        raise RuntimeError(f"Piper failed: {piper_result.stderr.decode('utf-8', errors='ignore')}")
    if not os.path.exists(temp_voice):
        raise RuntimeError("Piper ran but did not create audio file")

    mood = detect_mood(text)
    music_map = {"calm": CALM_MUSIC, "tense": TENSE_MUSIC, "inspirational": INSP_MUSIC}
    background_music = music_map[mood]

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", temp_voice,
        "-i", background_music,
        "-filter_complex",
        "[1:a]volume=0.3[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:a", "pcm_s16le",
        output_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")

    os.remove(temp_voice)
    os.remove(temp_text)
    debug("Audio generated successfully.")

# =========================
# MAIN PIPELINE
# =========================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No safety rule provided. Pass it as argument."}))
        sys.exit(1)

    rule = sys.argv[1]

    debug("Generating safety story...")
    story_en = generate_story(rule)

    debug("Translating to Hindi...")
    story_hi = translate_en_to_hi(story_en)

    file_id    = str(uuid.uuid4())
    audio_path = os.path.abspath(os.path.join(OUTPUT_DIR, f"{file_id}.wav"))

    debug("Generating audio narration...")
    generate_audio(story_hi, audio_path)

    result = {
        "story_en": story_en,
        "story_hi": story_hi,
        "audio_file": f"outputs/{file_id}.wav"
    }

    print(json.dumps(result, ensure_ascii=False))
