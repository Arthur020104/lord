from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.schedule_visit_chain_prompt import prompt_schedule_visit
node_schedule_visit = Node(prompt=prompt_schedule_visit, llm=generate_llm(temp=0, model=4), children={}, name="ScheduleVisit")