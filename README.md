# Isabella - The LLM Chatbot

Isabella is an AI-powered chatbot using Large Language Models (LLMs) for natural conversation, equipped with speech recognition and text-to-speech functionality. The system is organized into two main modules: Chatbot (text-based interaction) and SpeechRecog (speech handling), all managed from the main Isabella folder.

---

## 📁 Folder Structure

Isabella/
│
├── requirements.txt
│
├── Chatbot/
│ ├── build_llm.py
│ ├── llm_memory.py
│ ├── qa.py
│ └── run_cli.py
│
└── SpeechRecog/
├── speech_to_text.py
└── text_to_speech.py


---

## 🗂️ File Descriptions

### Isabella
- `requirements.txt`  
  Python dependencies for installing all necessary packages.

### Chatbot
- `build_llm.py`  
  Initializes the LLM model using environment variables and Langchain-Groq integration.
- `llm_memory.py`  
  Builds and manages conversation memory with buffer support for natural chat history.
- `qa.py`  
  Handles interactions with the LLM, using stored memory for human-like, context-aware responses.
- `run_cli.py`  
  Command-line interface to interact with Isabella via text.

### SpeechRecog
- `speech_to_text.py`  
  Real-time microphone listening to convert speech to text; handles ambient noise and errors gracefully.
- `text_to_speech.py`  
  Converts text responses to speech using gTTS and VLC for audio playback.

---

## ⚙️ Installation

1. **Clone or Download the Project**
    ```
    git clone <your-repo-url>
    cd Isabella
    ```

2. **Install Python Dependencies**
    ```
    pip install -r requirements.txt
    ```

3. **Environment Setup**
    - Add a `.env` file to store necessary API keys and model variables (see `build_llm.py` and Langchain-Groq documentation).

---

## 🚀 Usage

### Text Chatbot (CLI)
1. Go to the Chatbot directory:
    ```
    cd Chatbot
    ```
2. Run the CLI:
    ```
    python run_cli.py
    ```
3. Type messages or `exit` to quit.

### Speech Recognition & TTS
1. Go to the SpeechRecog directory:
    ```
    cd ../SpeechRecog
    ```
2. **Speech-to-Text**
    ```
    python speech_to_text.py
    ```
3. **Text-to-Speech**
    ```
    from text_to_speech import speak_text
    speak_text("Hello, this is Isabella!")
    ```

---

## 🛠️ Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies:
    ```
    langchain
    langgraph
    langchain-groq
    ipykernel
    python-dotenv
    openai
    pyttsx3
    gTTS
    pyaudio
    speechrecognition
    sounddevice
    numpy
    scipy
    pygame
    python-vlc
    ```

---

## 📝 Notes

- Ensure you have VLC installed for audio playback (used in `text_to_speech.py`).  
- Customize environment variables in `.env` as needed (API keys, model selection, etc).

---

## 💡 Credits

Developed using Langchain, Groq, SpeechRecognition, gTTS, and supporting Python libraries.
