import os
import re
import io
import requests
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play

# -------------------------------
# FORCE ffmpeg & ffprobe paths
# -------------------------------
ffmpeg_path = r"C:\Users\srija\Downloads\ffmpeg-8.0-essentials_build\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\srija\Downloads\ffmpeg-8.0-essentials_build\ffmpeg-8.0-essentials_build\bin\ffprobe.exe"

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = ffprobe_path

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError("❌ ELEVENLABS_API_KEY not found. Add it in your .env file!")

voice_id = "1qEiC6qsybMkmnNdVMbK"  # Jessica’s voice ID
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "xi-api-key": api_key,
    "Accept": "audio/mpeg",   # <- ✅ force MP3, works reliably
    "Content-Type": "application/json"
}

def speak_text(text: str):
    text = re.sub(r"\(.*?\)", "", text).strip()
    data = {"text": text, "model_id": "eleven_monolingual_v1"}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print("❌ API Error:", response.status_code, response.text)
        return

    try:
        # ✅ Load MP3, not WAV
        audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        louder = audio + 5
        print("🔊 Playing Jessica's voice...")
        play(louder)
        print("✅ Playback finished.")
    except Exception as e:
        print("❌ Playback Error:", e)

# -------------------------------
# Test Run
# -------------------------------
speak_text("Hello there! Jessica is now speaking! How can i help you")
