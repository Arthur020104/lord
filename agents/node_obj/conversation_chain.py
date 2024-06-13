from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.conversation_chain_prompt import conversation_prompt

conversation_chain = Node(
    prompt=conversation_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="ConversationChain", 
    property_info_key=['Resumo_en0', 'localizacao']#['nome','torres', 'andares_por_torre', 'localizacao','seguranca','amenidades','apartamentos']
    )