# build_llm.py
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

def build_llm():
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b") 
    # If ChatGroq supports max_tokens, keep responses short; otherwise rely on prompt.
    try:
        return ChatGroq(model=model, temperature=0.2, max_tokens=128)
    except TypeError:
        return ChatGroq(model=model, temperature=0.2)
