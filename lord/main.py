from langchain.schema.output_parser import StrOutputParser
import json
from AgentBuild.Memory.CustomBuffer import CustomConversationTokenBufferMemory
from lord.prompts.manager import manager_prompt
from lord.informacao_propriedade import empreendimento
#importing nodes
from lord.node_obj.schedule_visit_chain import node_schedule_visit
from lord.node_obj.end_of_conversation_user_no_time import end_of_conversation_user_no_time
from lord.node_obj.conversation_chain import conversation_chain
from lord.node_obj.start_conversation_chain import start_conversation_chain
from lord.node_obj.amenities_chain import amenities_chain
from lord.node_obj.apartments_chain import apartments_chain
from lord.node_obj.indication_chain import indication_chain
from lord.node_obj.objection_chain import objection_chain
from lord.node_obj.location_chain import location_chain
from lord.LLM import generate_llm
from AgentBuild.Agent.Agent import Agent
from AgentBuild.OutputParser.ManagerJson import manager_parser, manager_output_parser_str
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
manager_prompt.add_message('system', manager_output_parser_str)
manager = manager_prompt.get_prompt()| generate_llm(temp=0, model=4) | manager_parser

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
    'LocationChain': location_chain,
}

agent = Agent(initial_node=start_conversation_chain, 
              all_nodes=all_nodes,
              memory=memory,
              agent_info=empreendimento,
              manager=manager,
              nodes_info=dict_base
              )

def call_current_node():
    return agent.call_current_node()
def process_user_input(user_input):
    return agent.process_user_input(user_input)

def delete_memory():
    return agent.delete_memory()

