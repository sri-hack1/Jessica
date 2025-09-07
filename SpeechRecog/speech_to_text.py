import os
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVEN_API_KEY:
    raise ValueError("❌ ELEVENLABS_API_KEY not found in .env file!")

STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def listen_microphone(samplerate: int = 44100, silence_threshold=500, silence_duration=6):
    """
    Record until user stops speaking (detected via silence), then send to ElevenLabs for transcription.
    - silence_threshold: RMS level to treat as silence
    - silence_duration: seconds of silence before stopping
    """
    print("🎙️ Listening... Start speaking (stop when you're done).")

    buffer = []
    silence_counter = 0
    chunk_size = int(0.3 * samplerate)  # 300ms chunks

    with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16") as stream:
        while True:
            chunk, _ = stream.read(chunk_size)
            buffer.append(chunk)

            rms = np.sqrt(np.mean(chunk**2))
            if rms < silence_threshold:
                silence_counter += chunk_size / samplerate
            else:
                silence_counter = 0

            # Stop if silence lasts long enough
            if silence_counter > silence_duration:
                break

    print("✅ Recording stopped.")

    # Combine all chunks
    audio_data = np.concatenate(buffer, axis=0)

    # Save temp WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_data, samplerate)
        audio_path = tmpfile.name

    # Send to ElevenLabs
    headers = {"xi-api-key": ELEVEN_API_KEY}
    files = {"file": open(audio_path, "rb")}
    data = {"model_id": "scribe_v1", "language_code": "en", "diarize": False, "tag_audio_events": False}

    # print("📡 Sending audio to ElevenLabs...")
    response = requests.post(STT_URL, headers=headers, files=files, data=data)

    if response.status_code == 200:
        result = response.json()
        # print("📝 Transcription:", result["text"])
        return result["text"]
    else:
        print("❌ API Error:", response.status_code, response.text)
        return None


# -------------------------------
# Example usage
# -------------------------------
# if __name__ == "__main__":
#     text = listen_microphone()
