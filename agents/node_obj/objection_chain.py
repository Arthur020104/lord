from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.objection_prompt import objection_prompt

amenities_chain = Node(
    prompt=objection_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="AmenitiesChain", 
    property_info_key=['nome','amenidades','construtora','localizacao','data_entrega']
    )