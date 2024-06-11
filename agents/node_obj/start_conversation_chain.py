from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.start_conversation_chain_prompt import prompt_inicial_conversation

start_conversation_chain = Node(
    llm=generate_llm(0, 4), 
    children={}, 
    prompt=prompt_inicial_conversation, 
    name="StartConversationChain",
    property_info_key=['nome','localizacao','construtora']
    )