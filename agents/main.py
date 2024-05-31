from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, MessagesPlaceholder
import sys
sys.path.append('../')
from memory.CustomBuffer import CustomConversationTokenBufferMemory
from agents.node import Node
from agents.askforinfoNode import AskForInfoNode
from agents.dataNode import DataNode
from agents.prompts.prompt import prompt_inicial_conversation, manager_prompt, conversation_prompt,prompt, prompt_user_with_no_time, prompt_schedule_visit,prompt_inicial_data_query,prompt_pricing
from secret.apiOpenAI import api_key
import json

# Initialize the LLM
llm = ChatOpenAI(api_key=api_key, temperature=0.0, model="gpt-4o")

# Initialize memory
memory = CustomConversationTokenBufferMemory(max_token_limit=2000, ia_key="ai", human_key="human", order=1)

# Property information
property_info = {
    "UnitType": "HOUSE",
    "ListingType": "USED",
    "State": "Minas Gerais",
    "City": "Uberlândia",
    "Neighborhood": "Jardim Karaíba",
    "Street": "Avenida Vereador Junior de Oliveira",
    "ZipCode": 38410665,
    "Title": "Casa Nova a Venda no Condomínio Dois Irmãos",
    "Price": 1700000,
    "CondominiumFee": 590.0,
    "UsableAreas": 206,
    "Bedrooms": 3,
    "Bathrooms": 3,
    "Suites": 3.0,
    "ParkingSpaces": 4.0
}

# Global dictionary
global dict_base
dict_base = {
    'chat_history': [],
    'nome_do_cliente': 'Arthur',
    'nome_da_imobiliaria': 'ginga imoveis',
    'property_info': property_info,
}

# Initialize manager and conversation chain
global ask_for_info
end_of_conversation_user_no_time = Node(llm=llm, prompt=prompt_user_with_no_time, children={}, name="EndOfConversationUserNoTime")
#llm_manager = ChatOpenAI(api_key=api_key, temperature=0.3, model="gpt-4o")
manager = LLMChain(prompt=manager_prompt, llm=llm)
node_schedule_visit = Node(prompt=prompt_schedule_visit, llm=llm, children={},name="ScheduleVisit")
llm_high_temp = ChatOpenAI(api_key=api_key, temperature=0.3, model="gpt-4o")
conversation_chain = Node(prompt=conversation_prompt, llm=llm_high_temp, children={},name="ConversationChain")
ask_for_info = AskForInfoNode(llm=llm, prompt=prompt, children={},name="AskForInfo")
pricing_node = Node(llm=llm, prompt=prompt_pricing, children={},name="PricingNode")

global node, start_conversation_chain
#Node(llm=llm, prompt=prompt,children={}) #
start_conversation_chain = Node(llm=llm, children={}, prompt=prompt_inicial_conversation,name="StartConversationChain")
node = start_conversation_chain
data_manager = DataNode(llm=llm, prompt=prompt_inicial_data_query,children={},name="DataManager", askfoinfo=ask_for_info)

all_nodes = {
    "AskForInfo": ask_for_info,
    "ConversationChain": conversation_chain,
    "DataManager": data_manager,
    "EndOfConversationUserNoTime": end_of_conversation_user_no_time,
    "ScheduleVisit": node_schedule_visit,
    "PricingNode": pricing_node,
    'StartConversationChain': start_conversation_chain
}
for node_name in all_nodes:
    cnode = all_nodes[node_name]
    for child_name in all_nodes:
        cnode.add_child(child_name,all_nodes[child_name])
    #print(f'\n\nNode{node_name} children: {cnode.get_children()}')


def call_current_node():
    global node, dict_base, last_output
    dict_base['chat_history'] = memory.get_memory_tuple()
    response = node.call_chain(dict_base)
    last_output = response['text']
    #print(ask_for_info.user_details)
    #print(f"\n\n\n\n {response}\n\n\n\n")
    return response

def process_user_input(input):
    global node, dict_base, last_output
    memory.add(human_input=input, ia_output=last_output)
    node.process_input(memory.get_memory()[-1])
    
    dict_base['chat_history'] = memory.get_memory_tuple()
    for i in range(3):
        try:
            node_called = manager.invoke({
            'chat_history': memory.get_memory_tuple(),
            'nodes': node.get_children().keys(),
            'current_node': node.get_name()
            })
            node_called = node_called['text']
            data_dict = json.loads(node_called)
            node_called = data_dict['node']
            if node_called != "Não existe":
                node = node.get_children()[node_called]
            break
        except:
            continue
def delete_memory():
    memory.delete_memory()
    global node, start_conversation_chain
    node = start_conversation_chain
    