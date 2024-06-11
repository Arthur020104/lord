from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.indication_prompt import indication_prompt

indication_chain = Node(
    prompt=indication_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="IndicationChain", 
    property_info_key=['nome','construtora']
    )