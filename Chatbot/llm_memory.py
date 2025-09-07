from langchain.memory import ConversationBufferMemory

def build_memory():
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    return memory
