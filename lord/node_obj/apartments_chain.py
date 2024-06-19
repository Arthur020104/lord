from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.apartments_chain_prompt import apartments_chain_prompt

apartments_chain = Node(
    prompt=apartments_chain_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="ApartmentsChain", 
    property_info_key=['torres', 'andares_por_torre', 'apartamentos', 'apartamentos_detalhados']
    )