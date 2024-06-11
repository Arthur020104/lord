from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.end_of_conversation_user_no_time_prompt import prompt_user_with_no_time

end_of_conversation_user_no_time = Node(
    llm=generate_llm(temp=0, model=4), 
    prompt=prompt_user_with_no_time, 
    children={}, 
    name="EndOfConversationUserNoTime",
    property_info_key=['nome']
    )