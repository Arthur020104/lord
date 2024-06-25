from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.pricing_chain_prompt import pricing_chain_prompt

pricing_chain = Node(
    prompt=pricing_chain_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="PricingChain", 
    property_info_key=['resumo_preco']
    )