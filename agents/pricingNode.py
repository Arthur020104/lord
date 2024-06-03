import os
import sys
from agents.node import Node
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from agents.prompts.string_prompts import basic_prompt
sys.path.append('../')
from secret.apiOpenAI import api_key as API_KEY

class PricingNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name):
        super().__init__(llm, children, prompt, name)
        self.verbose = True

    def call_chain(self, input_dict):
        try:
            tools = load_tools(["llm-math"], llm=ChatOpenAI(api_key=API_KEY, temperature=0.2, model="gpt-3.5-turbo"))
            agent = initialize_agent(llm=self.llm, tools=tools, prompt=basic_prompt, return_intermediate_steps=True, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=self.verbose)
            input_dict['system_prompt'] = self.prompt
            response = agent.invoke(input_dict)
            response['text'] = response['output']
            return response
        except Exception as e:
            print(f"Error in call_chain: {e}")
            return {"text": "An error occurred. Please try again later."}

