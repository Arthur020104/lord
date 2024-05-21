from agents.node import Node
from tools.math import math_tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
class PricingNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name):
        super().__init__(llm, children, prompt, name)

    def call_chain(self, input_dict):
        tools2 = [math_tool]
        agent2 = create_openai_functions_agent(llm=self.llm, tools=tools2, prompt=self.prompt)
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent2, tools=tools2, verbose=True
        )
        response = agent_chain.invoke(input_dict)
        print(response)
        return {'text':response['output']}



