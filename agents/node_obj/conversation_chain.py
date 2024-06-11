from agents.LLM import generate_llm
from agents.node import Node
from agents.prompts.node_prompts.conversation_chain_prompt import conversation_prompt

conversation_chain = Node(prompt=conversation_prompt, llm=generate_llm(temp=0,model=4), children={}, name="ConversationChain")