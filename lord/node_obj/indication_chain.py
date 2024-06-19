from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.indication_prompt import indication_prompt

indication_chain = Node(
    prompt=indication_prompt, 
    llm=generate_llm(temp=0,model=4), 
    children={}, 
    name="IndicationChain", 
    property_info_key=['nome','construtora']
    )