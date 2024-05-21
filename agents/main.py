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
    "Bathrooms": 2,
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
manager = LLMChain(prompt=manager_prompt, llm=llm)
node_schedule_visit = Node(prompt=prompt_schedule_visit, llm=llm, children={'EndOfConversationUserNoTime': end_of_conversation_user_no_time},name="ScheduleVisit")
llm_high_temp = ChatOpenAI(api_key=api_key, temperature=0.3, model="gpt-4o")
conversation_chain = Node(prompt=conversation_prompt, llm=llm_high_temp, children={'EndOfConversationUserNoTime': end_of_conversation_user_no_time, 'ScheduleVisit': node_schedule_visit},name="ConversationChain")
ask_for_info = AskForInfoNode(llm=llm, prompt=prompt, children={'EndOfConversationUserNoTime': end_of_conversation_user_no_time, 'ScheduleVisit': node_schedule_visit,'ConversationChain': conversation_chain},name="AskForInfo")
pricing_node = Node(llm=llm, prompt=prompt_pricing, children={},name="PricingNode")



global node, start_conversation_chain
#Node(llm=llm, prompt=prompt,children={}) #
start_conversation_chain = Node(llm=llm, children={"ConversationChain": conversation_chain, 'EndOfConversationUserNoTime': end_of_conversation_user_no_time, 'ScheduleVisit': node_schedule_visit}, prompt=prompt_inicial_conversation,name="StartConversationChain")
node = start_conversation_chain
data_manager = DataNode(llm=llm, prompt=prompt_inicial_data_query,children={'EndOfConversationUserNoTime': end_of_conversation_user_no_time, 'ScheduleVisit': node_schedule_visit, 'ConversationChain': conversation_chain, 'StartConversationChain': node},name="DataManager", askfoinfo=ask_for_info)

#conversation_chain.add_child('AskForInfo', ask_for_info)
conversation_chain.add_child('DataManager', data_manager)
conversation_chain.add_child('PricingNode', pricing_node)
conversation_chain.add_child('StartConversationChain', node)
ask_for_info.add_child('DataManager', data_manager)
ask_for_info.add_child("StartConversationChain", node)
ask_for_info.add_child('PricingNode', pricing_node)
node_schedule_visit.add_child('PricingNode', pricing_node)
node_schedule_visit.add_child('StartConversationChain', node)
node_schedule_visit.add_child('DataManager', data_manager)
node_schedule_visit.add_child('ConversationChain', conversation_chain)
end_of_conversation_user_no_time.add_child('StartConversationChain', node)
end_of_conversation_user_no_time.add_child('PricingNode', pricing_node)
end_of_conversation_user_no_time.add_child('ConversationChain', conversation_chain)
#end_of_conversation_user_no_time.add_child('AskForInfo', ask_for_info)
end_of_conversation_user_no_time.add_child('ScheduleVisit', node_schedule_visit)
end_of_conversation_user_no_time.add_child('DataManager', data_manager)
node.add_child('DataManager', data_manager)
node.add_child('PriceNode', pricing_node)



def call_current_node():
    global node, dict_base, last_output
    dict_base['chat_history'] = memory.get_memory_tuple()
    response = node.call_chain(dict_base)
    last_output = response['text']
    print(ask_for_info.user_details)
    return response

def process_user_input(input):
    global node, dict_base, last_output
    memory.add(human_input=input, ia_output=last_output)
    node.process_input(memory.get_memory()[-1])
    
    dict_base['chat_history'] = memory.get_memory_tuple()
    node_called = manager.invoke({
        'chat_history': memory.get_memory_tuple(),
        'nodes': node.get_children().keys(),
        'current_node': node.get_name()
    })
    print(node_called)
    node_called = node_called['text']
    print(node.get_children())
    print(f'Calling node: {node_called}')
    if node_called != "Não existe":
        node = node.get_children()[node_called]

if __name__ == '__main__':
    print(node.call_chain())

def delete_memory():
    memory.delete_memory()
    global node, start_conversation_chain
    node = start_conversation_chain
    