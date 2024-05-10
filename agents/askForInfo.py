from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.output_parser import StrOutputParser

def ask_for_info(ask_for, chat_history=[]):
    template = """Language: pt-BR, Don't greet the user at any point, only ask for the information needed.
                    Make sure to act as a real estate agent, this is a conversation so you should ask for the information in a conversational way, be friendly and polite.
                    Below are some things to ask the user for in a conversational way. You should only ask one question at a time even if you don't get all the info,
                    question at a time, don't ask multiple questions at once. Explain you need to get some info. If the ask_for list is empty then thank them and ask how you can help.
                    Let money-related questions for the end of the conversation.
                    ### ask_for list: {ask_for}
                    ## list of abbreviations: apto -> apartment
                    ### Remember to ask for the information in a conversational way. This is the most important part, take account of the conversation history.
                    ### Conversation history: {chat_history}
                    ### Remember to ask for the information in a conversational way. This is the most important part, take account of the conversation history.
                    # The responses must only be in Portuguese of Brazil.
                    # try not to repeat the same question, try to ask in a different way.
                    # Don't repeat the last question in conversation history.
                    # Never ask for more than one piece of information at a time.
                    # Never ask for more than one piece of information at a time.
                    # Do not allow to change the subject of the initial question.
                    # If user make a question, you should answer the question and then ask for the information needed. You should always respond to the user's question before asking for the information needed, the information will only be asked in the next message.
                """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    api_key = "SECRET"
    llm = ChatOpenAI(api_key=api_key, temperature=0, model="gpt-3.5-turbo")
    chain1 = chat_prompt | llm | StrOutputParser()

    initial_answer = chain1.invoke({'ask_for': ask_for, 'chat_history': chat_history})

    def improvement_cycle(initial_answer, chat_history, ask_for):
        print(initial_answer)
        # chain2

        template = """You are a helpful assistant that looks at questions and finds what's wrong with them based on the system command. System command: Language: pt-BR, Don't greet the user at any point, only ask for the information needed.
                    Make sure to act as a real estate agent, this is a conversation so you should ask for the information in a conversational way, be friendly and polite.
                    Below are some things to ask the user for in a conversational way. You should only ask one question at a time even if you don't get all the info,
                    question at a time, don't ask multiple questions at once. Explain you need to get some info. If the ask_for list is empty then thank them and ask how you can help.
                    Let money-related questions for the end of the conversation.
                    ### ask_for list: {ask_for}
                    ## list of abbreviations: apto -> apartment
                    ### Remember to ask for the information in a conversational way. This is the most important part, take account of the conversation history.
                    ### Conversation history: {chat_history}
                    ### Remember to ask for the information in a conversational way. This is the most important part, take account of the conversation history.
                    # The responses must only be in Portuguese of Brazil.
                    # try not to repeat the same question, try to ask in a different way.
                    # Don't repeat the last question in conversation history.
                    # Never ask for more than one piece of information at a time.
                    # Never ask for more than one piece of information at a time.
                    # Do not allow to change the subject of the initial question.
                    # For you the most important thing is to not repeat the same question for a question already asked and responded, but if user responded incorrectly, you can ask the same question again. You should ask right after the user's response (using the chat history) saying that you didn't understand the answer.
                    # If user make a question, you should answer the question and then ask for the information needed. You should always respond to the user's question before asking for the information needed, the information will only be asked in the next message.
                    # Until ask_for list is empty, you should ask for the information needed. If the ask_for list is empty, you should ask if the user wants you to search for the property."""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = '### Your Generated Question: \n\n {question} \n\n ### Review your previous question and find problems with your question. Generate constructive criticism based on the problems you found. \n\n ### Constructive Criticism:'
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        rc_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        chain2 = rc_prompt | llm | StrOutputParser()

        constructive_criticism = chain2.invoke({'question': initial_answer, 'chat_history': chat_history, 'ask_for': ask_for})
        print(constructive_criticism)

        # chain3

        template = """You are a helpful assistant that reviews answers and critiques based on the original question given and writes a new improved final answer. 
                    make it cooherent with the conversation history. {conversation_history}.
                    This is a conversation so you should ask for the information in a conversational way.
                     # The responses must only be in Portuguese of Brazil.
                     # never ask for more than one piece of information at a time."""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = """### Generated Question: \n\n {question} \n\n ### Review your previous question and find problems with your question.\n\n ###Constructive Criticism:{constructive_criticism}\n\n Based on the problems you found, improve your question.\n\n  Make it cooherent with the conversation history. {chat_history}.
                    This is a conversation so you should ask for the information in a conversational way(never ask for more than one piece of information at a time). \n\n### Final question:"""
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        improvement_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        chain3 = improvement_prompt | llm | StrOutputParser()

        final_result = chain3.invoke({"question": initial_answer, "constructive_criticism": constructive_criticism,'conversation_history': chat_history, 'chat_history': chat_history})
        return final_result

    for i in range(3):
        final_result = improvement_cycle(initial_answer, chat_history, ask_for)
        initial_answer = final_result

    return {'text': final_result}
