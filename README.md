# 🎙️ VoiceLog — AI Conversation Recorder

A full-stack web application for recording conversations, detecting multiple speakers, and generating AI transcripts.

---

## Features

- 🎤 **Browser Recording** — Record directly from microphone via Web Audio API
- 👥 **Speaker Detection** — Automatic multi-speaker detection using librosa pitch/energy analysis (or pyannote.audio with HuggingFace token)
- 📝 **AI Transcription** — Powered by OpenAI Whisper (faster-whisper, runs locally/free)
- 📊 **Session Dashboard** — Track sessions from Created → Recording → Uploaded → In Progress → Completed
- 📱 **App Simulator** — Mobile-like recording interface
- 💬 **Transcript View** — Conversation bubble UI with speaker badges and timestamps
- 🚀 **Render Compatible** — Deploys to Render free tier

---

## Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install FFmpeg (required for audio conversion)
# macOS:
brew install ffmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg
# Windows: download from https://ffmpeg.org/download.html

# 4. Run the app
python app.py
```

Visit: http://localhost:5000

**Demo Login:** `demo@test.com` / `demo123`

---

## Project Structure

```
conversation-recorder/
├── app.py                    # Flask app factory + entry point
├── models/
│   ├── user.py               # User model
│   ├── session.py            # Session model
│   └── recording.py          # Recording model
├── routes/
│   ├── auth_routes.py        # Login/logout
│   ├── main_routes.py        # Page routes
│   ├── session_routes.py     # Session CRUD API
│   └── recording_routes.py   # Upload + async processing
├── services/
│   ├── audio_service.py      # FFmpeg WAV conversion
│   ├── transcription_service.py  # Whisper transcription
│   └── speaker_service.py    # Speaker diarization
├── static/
│   ├── css/style.css         # Full design system
│   └── js/
│       ├── app.js            # Shared utilities
│       ├── session.js        # Dashboard session management
│       └── recorder.js       # Recording + waveform + upload
└── templates/
    ├── index.html            # Home page
    ├── login.html            # Auth page
    ├── dashboard.html        # Session management
    ├── app_view.html         # Mobile recording simulator
    ├── transcript.html       # Conversation transcript view
    └── session_details.html  # Session detail view
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key...` | Flask session secret (change in production!) |
| `DATABASE_URL` | `sqlite:///database/app.db` | Database URL (PostgreSQL for production) |
| `WHISPER_MODEL` | `base` | Whisper model size: `tiny`, `base`, `small`, `medium` |
| `HUGGINGFACE_TOKEN` | — | Optional: enables pyannote.audio for better speaker detection |

---

## Speaker Detection

Two modes available:

### Mode 1: Energy/Pitch Analysis (Default — No API needed)
Uses `librosa` to analyze pitch mean and RMS energy per segment. Clusters segments into speakers by pitch range. Works well for conversations with audibly different voices.

### Mode 2: pyannote.audio (Optional — Best accuracy)
1. Accept terms at https://huggingface.co/pyannote/speaker-diarization-3.1
2. Get a HuggingFace token at https://huggingface.co/settings/tokens
3. Set `HUGGINGFACE_TOKEN` env var
4. Uncomment pyannote lines in `requirements.txt` and reinstall

---

## Deploy to Render

1. Push this project to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — click Deploy
5. Set `SECRET_KEY` env var in Render dashboard

> **Note:** Free Render instances spin down after inactivity. First request after spindown takes ~30s.

---

## API Endpoints

### Auth
- `POST /auth/login` — Login (JSON or form)
- `GET /auth/logout` — Logout

### Sessions
- `GET /sessions/` — List all sessions for current user
- `POST /sessions/create` — Create new session
- `GET /sessions/<id>` — Get session details
- `PATCH /sessions/<id>/status` — Update session status

### Recordings
- `POST /record/upload` — Upload audio file (multipart/form-data)
  - Fields: `audio` (file), `session_id`
- `GET /record/status/<id>` — Poll processing status
- `GET /record/transcript/<id>` — Get transcript data

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Transcription | faster-whisper (Whisper base/small) |
| Speaker Detection | librosa / pyannote.audio |
| Audio Processing | FFmpeg + pydub |
| Frontend | Vanilla JS + CSS (glassmorphism) |
| Fonts | Syne + Space Grotesk |
| Hosting | Render |

---

## License

MIT — free to use and modify.
