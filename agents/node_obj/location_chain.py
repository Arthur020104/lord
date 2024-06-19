from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.location_prompt import location_prompt

location_chain = Node(
    llm=generate_llm(temp=0, model=4), 
    prompt=location_prompt, 
    children={}, 
    name="LocationChain",
    property_info_key=['localizacao', 'construtora', 'nome']
    )