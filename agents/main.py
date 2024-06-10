import os
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, MessagesPlaceholder
import sys
import json
from memory.CustomBuffer import CustomConversationTokenBufferMemory
from agents.node import Node
from agents.askforinfoNode import AskForInfoNode
from agents.dataNode import DataNode
from agents.prompts.prompt import (prompt_inicial_conversation, manager_prompt, conversation_prompt,
                                   prompt, prompt_user_with_no_time, prompt_schedule_visit,
                                   prompt_inicial_data_query, prompt_pricing)

from secret.apiOpenAI import api_key as API_KEY
from agents.informacao_propriedade import empreendimento
model4o = "gpt-4o"
model35_turbo = "gpt-3.5-turbo"
# Initialize the LLM
llm = ChatOpenAI(api_key=API_KEY, temperature=0.0, model=model4o)

# Initialize memory
memory = CustomConversationTokenBufferMemory(max_token_limit=2000, ia_key="ai", human_key="human", order=1)

# Property information
property_info = empreendimento

# Global dictionary
dict_base = {
    'chat_history': [],
    'nome_do_cliente': 'Arthur',
    'nome_da_imobiliaria': 'ginga imoveis',
    'property_info': empreendimento,
}

# Initialize nodes
end_of_conversation_user_no_time = Node(llm=llm, prompt=prompt_user_with_no_time, children={}, name="EndOfConversationUserNoTime")
manager_llm = ChatOpenAI(api_key=API_KEY, temperature=0.0, model=model4o)
manager = LLMChain(prompt=manager_prompt, llm=manager_llm)
node_schedule_visit = Node(prompt=prompt_schedule_visit, llm=llm, children={}, name="ScheduleVisit")
llm_high_temp = ChatOpenAI(api_key=API_KEY, temperature=0.2, model=model4o)
conversation_chain = Node(prompt=conversation_prompt, llm=llm_high_temp, children={}, name="ConversationChain")
ask_for_info = AskForInfoNode(llm=llm, prompt=prompt, children={}, name="AskForInfo")
pricing_node = Node(llm=llm, prompt=prompt_pricing, children={}, name="PricingNode")

# Initialize start and data manager nodes
start_conversation_chain = Node(llm=llm, children={}, prompt=prompt_inicial_conversation, name="StartConversationChain")
data_manager = DataNode(llm=llm, prompt=prompt_inicial_data_query, children={}, name="DataManager", askfoinfo=ask_for_info)

# Create a dictionary for all nodes
all_nodes = {
   #"AskForInfo": ask_for_info,
    "ConversationChain": conversation_chain,
   # "DataManager": data_manager,
    "EndOfConversationUserNoTime": end_of_conversation_user_no_time,
    "ScheduleVisit": node_schedule_visit,
    #"PricingNode": pricing_node,
    'StartConversationChain': start_conversation_chain
}

# Add children to nodes
for node_name, cnode in all_nodes.items():
    for child_name, child_node in all_nodes.items():
        cnode.add_child(child_name, child_node)

# Global node variable
node = start_conversation_chain

def call_current_node():
    global node, dict_base, last_output
    try:
        dict_base['chat_history'] = memory.get_memory_tuple()
        dict_base['property_info'] = node.filter_property_info(property_info)
        response = node.call_chain(dict_base)
        last_output = response['text']
        return response
    except Exception as e:
        print(f"Error in call_current_node: {e}")
        return {"text": "An error occurred. Please try again later."}

def process_user_input(user_input):
    global node, dict_base, last_output
    try:
        memory.add(human_input=user_input, ia_output=last_output)
        node.process_input(memory.get_memory()[-1])
        
        dict_base['chat_history'] = memory.get_memory_tuple()
        for _ in range(3):
            try:
                node_called = manager.invoke({
                    'chat_history': memory.get_memory_tuple(),
                    'nodes': list(node.get_children().keys()),
                    'current_node': node.get_name()
                })
                node_called = node_called['text']
                data_dict = json.loads(node_called)
                node_called = data_dict['node']
                print(f"Node called: {node_called}")
                if node_called != "Não existe":
                    node = node.get_children()[node_called]
                break
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except KeyError as e:
                print(f"Key error: {e}")
    except Exception as e:
        print(f"Error in process_user_input: {e}")

def delete_memory():
    global node, start_conversation_chain
    memory.delete_memory()
    node = start_conversation_chain
    print("Memory deleted and conversation reset.")

