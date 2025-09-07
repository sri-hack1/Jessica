# run_cli.py
from build_llm import build_llm
from qa import ask_jessica

def main():
    llm = build_llm()
    print("Jarvis (basic QA). Type 'exit' to quit.")
    while True:
        q = str(input("You: ").strip())
        if q.lower() in {"exit", "quit"}:
            print("Jarvis: Bye.")
            break
        try:
            ans = ask_jessica(llm, q)
            print("Jarvis:", ans)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
