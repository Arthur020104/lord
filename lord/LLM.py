from secret.apiOpenAI import api_key as API_KEY
from langchain_openai import ChatOpenAI

model4o = "gpt-4o"
model35_turbo = "gpt-3.5-turbo"

def generate_llm(temp:float = 0, model:float= 3.5):
    if model == 4:
        return ChatOpenAI(api_key=API_KEY, temperature=temp, model=model4o)
    elif model == 3.5:
        return ChatOpenAI(api_key=API_KEY, temperature=temp, model=model35_turbo)
    else:
        raise ValueError("Model not found")
