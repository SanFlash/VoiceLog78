import re
from datetime import datetime

def format_duration(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def safe_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def now_str() -> str:
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
