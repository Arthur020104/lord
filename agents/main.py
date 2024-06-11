from langchain.schema.output_parser import StrOutputParser
import json
from memory.CustomBuffer import CustomConversationTokenBufferMemory
from agents.prompts.prompt import manager_prompt
from agents.informacao_propriedade import empreendimento
#importing nodes
from agents.node_obj.schedule_visit_chain import node_schedule_visit
from agents.node_obj.end_of_conversation_user_no_time import end_of_conversation_user_no_time
from agents.node_obj.conversation_chain import conversation_chain
from agents.node_obj.start_conversation_chain import start_conversation_chain
from agents.node_obj.amenities_chain import amenities_chain
from agents.node_obj.apartments_chain import apartments_chain
from agents.node_obj.indication_chain import indication_chain
from agents.node_obj.objection_chain import objection_chain
from agents.LLM import generate_llm

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

manager = manager_prompt| generate_llm(temp=0, model=4) | StrOutputParser()

#ask_for_info = AskForInfoNode(llm=llm, prompt=prompt, children={}, name="AskForInfo")
#pricing_node = Node(llm=llm, prompt=prompt_pricing, children={}, name="PricingNode")
#data_manager = DataNode(llm=llm, prompt=prompt_inicial_data_query, children={}, name="DataManager", askfoinfo=ask_for_info)

# Create a dictionary for all nodes
all_nodes = {
    'StartConversationChain': start_conversation_chain,
    "ConversationChain": conversation_chain,
    "ScheduleVisit": node_schedule_visit,
    "EndOfConversationUserNoTime": end_of_conversation_user_no_time,
    "AmenitiesChain": amenities_chain,
    "ApartmentsChain": apartments_chain,
    "IndicationChain": indication_chain,
    "ObjectionChain": objection_chain,
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
        dict_base['property_info'] = node.filter_property_info(empreendimento)
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
                node_called = node_called
                data_dict = json.loads(node_called)
                node_called = data_dict['node']
                print(f"Node called: {node_called}, why called: {data_dict['answer']}")
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

