from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.start_conversation_chain_prompt import prompt_inicial_conversation

start_conversation_chain = Node(
    llm=generate_llm(0, 4), 
    children={}, 
    prompt=prompt_inicial_conversation, 
    name="StartConversationChain",
    property_info_key=['nome','localizacao','construtora']
    )