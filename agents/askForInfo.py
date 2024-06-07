import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from secret.apiOpenAI import api_key
sys.path.append('../')
from agents.prompts.askforinfo_prompts import basic_prompt, prompt_for_review, prompt_for_final_answer

def ask_for_info(ask_for, llm, chat_history=None):
    if chat_history is None:
        chat_history = []

    initial_chain = basic_prompt | llm | StrOutputParser()
    answer = initial_chain.invoke({'ask_for': ask_for, 'chat_history': chat_history})


    return {'text': answer}
