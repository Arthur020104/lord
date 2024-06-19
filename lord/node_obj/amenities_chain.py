from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.amenities_prompt import amenities_prompt

amenities_chain = Node(
    prompt=amenities_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="AmenitiesChain", 
    property_info_key=['nome', 'seguranca','amenidades']
    )