
from Chatbot.build_llm import build_llm
from Chatbot.qa import ask_jessica
from SpeechRecog.speech_to_text import listen_microphone
from SpeechRecog.text_to_speech import speak_text
import warnings

def build_assistant():
    warnings.filterwarnings("ignore")
    llm = build_llm()
    print("Jessica (basic QA). Type 'exit' to quit.")
    while True:
        # q = str(input("You: ").strip())
        q = listen_microphone()
        
        if q.lower() in {"exit", "quit", "bye"}:
            print("Jessica: Bye.")
            speak_text("Bye Sir")
            break
        try:
            ans = ask_jessica(llm, q)
            print("Jessica:", ans)
            speak_text(ans)
        except Exception as e:
            print("Error:", e)
            
build_assistant()
