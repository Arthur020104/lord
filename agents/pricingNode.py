import sys
sys.path.append('../')
from agents.node import Node
from langchain.agents import AgentExecutor
from secret.apiOpenAI import api_key
# from tools.math import execute_code_tool as math_tool
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

class PricingNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name):
        super().__init__(llm, children, prompt, name)
        self.verbose = True

    def call_chain(self, input_dict):
        tools = load_tools(["llm-math"], llm=ChatOpenAI(api_key=api_key, temperature=0.2, model="gpt-3.5-turbo"))

        agent2 = initialize_agent(llm=self.llm, tools=tools, prompt=self.prompt,return_intermediate_steps=True,agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=self.verbose)
        response = agent2.invoke(input_dict)
        response['text'] = response['output']
        return response
#calcule quanto tempo para paga essa cas com parcelas de 10 mil