import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from secret.apiOpenAI import api_key
sys.path.append('../')
from agents.prompts.askforinfo_prompts import basic_prompt, prompt_for_review, prompt_for_final_answer

def ask_for_info(ask_for, chat_history=None, gpt_model="gpt-3.5-turbo", improvement_cycles=2):
    if chat_history is None:
        chat_history = []

    # Initialize the language model
    llm = ChatOpenAI(api_key=api_key, temperature=0, model=gpt_model)
    
    # Define the initial chain
    initial_chain = basic_prompt | llm | StrOutputParser()
    initial_answer = initial_chain.invoke({'ask_for': ask_for, 'chat_history': chat_history})

    def improvement_cycle(answer, chat_history, ask_for):
        review_chain = prompt_for_review | llm | StrOutputParser()
        constructive_criticism = review_chain.invoke({'question': answer, 'chat_history': chat_history, 'ask_for': ask_for})
        print(constructive_criticism)
        
        final_chain = prompt_for_final_answer | llm | StrOutputParser()
        final_result = final_chain.invoke({
            'question': answer,
            'constructive_criticism': constructive_criticism,
            'chat_history': chat_history
        })
        return final_result

    # Run improvement cycles
    final_result = initial_answer
    for _ in range(improvement_cycles):
        final_result = improvement_cycle(final_result, chat_history, ask_for)

    return {'text': final_result}
