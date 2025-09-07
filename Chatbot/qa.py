# qa.py
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .llm_memory import build_memory

memory = build_memory()

def ask_jessica(llm, question: str) -> str:
    system = SystemMessage(
        content=(
            """ You are a Jarvis assistant, you know well how that was in Marvel movies,
            I want you to give human like response for the questions given for you.
            Sometimes initiate in the conversation but not give a large or medium reponse.
            Keep it short along with Human behaviour. According to the conversation or talk
            keep your mood accordingly. But most of the time keep yourself funnier
            Just again make sure don't give response like AI because you know how long they 
            give their response.
            
            So overall just give a human like response not an AI like and along don't give lengthy 
            reponses. Don't use emoji's and all anything which human don't speak while conversation like 
            he nevers tell "laughing emoji with showing hands". Do not do that anyhow.
            """
        )
    )

    # add user message into memory
    memory.chat_memory.add_message(HumanMessage(content=question))

    # get full conversation history from memory
    history = memory.load_memory_variables({})["history"]

    # final messages = system prompt + history
    messages = [system] + history

    # send to LLM
    response = llm.invoke(messages)

    # Save AI’s reply back into memory
    memory.chat_memory.add_message(AIMessage(content=response.content))

    return response.content
