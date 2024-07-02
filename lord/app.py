import sys
import os
sys.path.append("../")
sys.path.append("./")
import uuid
from flask import Flask, request, jsonify
from functools import wraps
from collections import defaultdict
from langchain.schema.output_parser import StrOutputParser
# Importações dos módulos do projeto
from AgentBuild.Memory.CustomBuffer import CustomConversationTokenBufferMemory
from AgentBuild.Agent.Agent import Agent
from AgentBuild.OutputParser.ManagerJson import manager_parser, manager_output_parser_str
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
from lord.FakeResponse.FakeResponse import FakeResponse

app = Flask(__name__)

# Inicializando memória do agente
memory = CustomConversationTokenBufferMemory(max_token_limit=2000, ia_key="ai", human_key="human", order=1)

# Informações do empreendimento
property_info = empreendimento

# Dicionário base da aplicação
dict_base = {
    'chat_history': defaultdict(list),
    'nome_do_cliente': 'Arthur',
    'nome_da_imobiliaria': 'ginga imoveis',
    'property_info': empreendimento,
    'common_prompt': """Never write number as digits, always write them as words. For example, write "cinco" instead of "5".
    Never say float numbers, always round them to the nearest whole number. For example, write "cinco" instead of "5.5".
    Always write the currency in full. For example, write "reais" instead of "R$".
    Always write the unit of measurement in full. For example, write "metros quadrados" instead of "m²".
    Always write in correct PT-BR with proper punctuation and grammar.
    Never use abbreviations; use only complete words.
    Always keep the conversation natural and friendly.
    Don't write more than 35 words in a single message.
    Pay attention to your previous messages to not repeat yourself. Never repeat yourself.
    """,
    'manager_thought': ''
}

# Configurando o manager
manager_prompt.add_message('system', manager_output_parser_str)
manager = manager_prompt.get_prompt() | generate_llm(temp=0, model=4) | manager_parser

# Dicionário com todos os nós
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

# Inicializando o agente
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

# Middleware para controle de conversações por token
conversation_map = defaultdict(lambda: {'last_user_input': '', 'last_llm_response': ''})

def ensure_unique_conversation_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 400
        kwargs['conversation_data'] = conversation_map[token]
        return func(*args, **kwargs)
    return wrapper

# Função para gerar um token único
def generate_token():
    return str(uuid.uuid4())

# Endpoint para iniciar uma nova conversa e obter um token
@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    token = generate_token()
    conversation_map[token]  # Inicializa a conversa
    return jsonify({'token': token})

# Helper function to process user input
def handle_user_input(conversation_data, user_input):
    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400

    conversation_data['last_user_input'] = user_input
    agent.process_user_input(user_input)

    return jsonify({'message': 'User input processed successfully'})

# Endpoint para processar a entrada do usuário
@app.route('/process_user_input', methods=['POST'])
@ensure_unique_conversation_token
def process_user_input_endpoint(conversation_data):
    user_input = request.data.decode('utf-8')
    return handle_user_input(conversation_data, user_input)

# Endpoint para chamar o nó atual do agente
@app.route('/call_current_node', methods=['POST'])
@ensure_unique_conversation_token
def call_current_node_endpoint(conversation_data):
    new_response = False

    if fake_response.get_response(user_input=conversation_data['last_user_input'], current_node=agent.get_current_node()):
        last_llm_response = {'text': fake_response.get_response(user_input=conversation_data['last_user_input'], current_node=agent.get_current_node())}
        agent.last_output = last_llm_response['text']
    else:
        new_response = True
        last_llm_response = agent.call_current_node()

    if conversation_data['last_user_input'] and new_response:
        fake_response.add_response(conversation_data['last_user_input'], last_llm_response['text'], agent.get_current_node())

    conversation_data['last_llm_response'] = last_llm_response
    return jsonify(last_llm_response)

# Endpoint para reiniciar a memória do agente
@app.route('/reset_memory', methods=['POST'])
@ensure_unique_conversation_token
def reset_memory_endpoint(conversation_data):
    agent.delete_memory()

    conversation_data['last_user_input'] = ''
    conversation_data['last_llm_response'] = ''

    return jsonify({'message': 'Agent memory reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
