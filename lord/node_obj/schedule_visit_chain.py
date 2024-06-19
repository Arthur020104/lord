from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.schedule_visit_chain_prompt import prompt_schedule_visit
node_schedule_visit = Node(
    prompt=prompt_schedule_visit, 
    llm=generate_llm(temp=0, model=4), 
    children={}, 
    name="ScheduleVisit",
    property_info_key=['localizacao']
    )