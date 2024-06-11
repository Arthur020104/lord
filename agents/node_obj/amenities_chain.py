from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.amenities_prompt import amenitites_prompt

amenities_chain = Node(
    prompt=amenitites_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="AmenitiesChain", 
    property_info_key=['nome', 'seguranca','amenidades']
    )