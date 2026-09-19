import os
from langchain_openai import ChatOpenAI

def model():
    return ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'), temperature=0)
