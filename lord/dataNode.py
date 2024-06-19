import os
import sys
from AgentBuild.Node.node import Node
from AgentBuild.Prompt.prompt import prompt_afther_data_query
from langchain.chains.llm import LLMChain
from tools.dataManager import generate_and_execute_query
sys.path.append('../')
from secret.apiOpenAI import api_key as API_KEY
class DataNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name, askfoinfo):
        super().__init__(llm, children, prompt, name)
        self.askforinfo = askfoinfo
        
    def call_chain(self, input_dict):
        try:
            response = self.chain.invoke(input_dict)
            print(response)
            response_text = response['text']
            resposta = generate_and_execute_query(response_text)
            
            afther_chain = LLMChain(prompt=prompt_afther_data_query, llm=self.llm)
            input_dict['input'] = resposta
            final_response = afther_chain.invoke(input_dict)
            print(final_response)
            return final_response
        except Exception as e:
            print(f"Error in call_chain: {e}")
            return {"text": "An error occurred. Please try again later."}