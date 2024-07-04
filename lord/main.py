import json
import os
from langchain.schema.output_parser import StrOutputParser
from AgentBuild.Memory.CustomBuffer import CustomConversationTokenBufferMemory
from lord.prompts.manager import manager_prompt
from lord.informacao_propriedade import empreendimento
from lord.node_obj.schedule_visit_chain import node_schedule_visit
from lord.node_obj.end_of_conversation_user_no_time import end_of_conversation_user_no_time
from lord.node_obj.conversation_chain import conversation_chain
from lord.node_obj.start_conversation_chain import start_conversation_chain
from lord.node_obj.amenities_chain import amenities_chain
from lord.node_obj.apartments_chain import apartments_chain
from lord.node_obj.indication_chain import indication_chain
from lord.node_obj.objection_chain import objection_chain
from lord.node_obj.location_chain import location_chain
from lord.node_obj.pricing import pricing_chain
from lord.LLM import generate_llm
from AgentBuild.Agent.Agent import Agent
from AgentBuild.OutputParser.ManagerJson import manager_parser, manager_output_parser_str
from lord.FakeResponse.FakeResponse import FakeResponse

# Inicializando memoria do agente
memory = CustomConversationTokenBufferMemory(max_token_limit=2000, ia_key="ai", human_key="human", order=1)

# Informações do empreendimento
property_info = empreendimento

# Dicionario base da aplicacao, contem informacoes que sao passadas para todos os nos. Voce pode definir essas chaves na criacao do prompt
dict_base = {
    'chat_history': [],
    'nome_do_cliente': 'Arthur',
    'nome_da_imobiliaria': 'ginga imoveis',
    'property_info': empreendimento,
    'common_prompt': """Never write number as digits, always write them as words. For example, write "cinco" instead of "5".
    Never say float numbers, always round them to the nearest whole number. For example, write "cinco" instead of "5.5".
    Always write the currency in full. For example, write "reais" instead of "R$".
    Make sure the current message connects with the previous ones naturally.
    Never write more than one paragraph in a single message.
    Always write the unit of measurement in full. For example, write "metros quadrados" instead of "m²".
    Always write in correct PT-BR with proper punctuation and grammar.
    Never use abbreviations; use only complete words.
    Always kepp the conversation natural and friendly.
    Dont write more than 35 words in a single message.
    [RULES] The rules must always be followed your you will be penalized:
    1. Never repeat yourself.
    2. Pay attention to your previous messages to not repeat yourself. Never repeat yourself.
    """,
    'manager_thought': ''
}

# Configurando o manager
manager_prompt.add_message('system', manager_output_parser_str)
manager = manager_prompt.get_prompt() | generate_llm(temp=0, model=4) | manager_parser

# Dicionario com todos os nós
all_nodes = {
    'StartConversationChain': start_conversation_chain,
    'ConversationChain': conversation_chain,
    'ScheduleVisit': node_schedule_visit,
    'EndOfConversationUserNoTime': end_of_conversation_user_no_time,
    'AmenitiesChain': amenities_chain,
    'ApartmentsChain': apartments_chain,
    'IndicationChain': indication_chain,
    'ObjectionChain': objection_chain,
    'LocationChain': location_chain,
    'PricingChain': pricing_chain
}

# Initializando o agente
agent = Agent(
    initial_node=start_conversation_chain,
    all_nodes=all_nodes,
    memory=memory,
    agent_info=empreendimento,
    manager=manager,
    nodes_info=dict_base,
    verbose_prices=True
)

# Adicionando FakeResponse
csv_reference = os.path.abspath('lord/FakeResponse/data.csv')
fake_response = FakeResponse(csv_reference)

# Variáveis globais para armazenar a última entrada do usuário e a última resposta do LLM
last_user_input = ''
last_llm_response = ''

# Função para chamar o nó atual do agente
def call_current_node():
    global last_llm_response  # Permite modificar a variável global last_llm_response
    new_response = False  # Variável para rastrear se uma nova resposta foi gerada

    # Verifica se existe uma resposta fake para a última entrada do usuário e o nó atual do agente
    if fake_response.get_response(user_input=last_user_input, current_node=agent.get_current_node()):
        # Se houver uma resposta fake, define last_llm_response com essa resposta
        last_llm_response = {'text': fake_response.get_response(user_input=last_user_input, current_node=agent.get_current_node())}
        agent.last_output = last_llm_response['text']  # Atualiza a última saída do agente, isso será útil para o Agente consiguir gerenciar a memória
    else:
        new_response = True  # Indica que uma nova resposta foi gerada
        last_llm_response = agent.call_current_node()  # Chama o nó atual do agente para obter uma nova resposta
    
    # Se houver uma última entrada do usuário e uma nova resposta foi gerada
    if last_user_input and new_response:
        # Adiciona a nova resposta fake ao fake_response
        fake_response.add_response(last_user_input, last_llm_response['text'], agent.get_current_node())
    
    return last_llm_response  # Retorna a última resposta do LLM

# Função para processar a entrada do usuário
def process_user_input(user_input):
    global last_user_input  # Permite modificar a variável global last_user_input
    last_user_input = user_input  # Atualiza a última entrada do usuário
    return agent.process_user_input(user_input)  # Processa a entrada do usuário pelo agente

# Função para deletar a memória do agente
def delete_memory():
    global last_user_input, last_llm_response  # Permite modificar as variáveis globais last_user_input e last_llm_response
    last_user_input = ''  # Reseta a última entrada do usuário
    last_llm_response = ''  # Reseta a última resposta do LLM
    return agent.delete_memory()  # Chama a função de deletar memória do agente
