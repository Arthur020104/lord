from lord.LLM import generate_llm
from AgentBuild.Node.node import Node
from lord.prompts.node_prompts.end_of_conversation_user_no_time_prompt import prompt_user_with_no_time

end_of_conversation_user_no_time = Node(
    llm=generate_llm(temp=0, model=4), 
    prompt=prompt_user_with_no_time, 
    children={}, 
    name="EndOfConversationUserNoTime",
    property_info_key=['nome']
    )