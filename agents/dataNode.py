from agents.node import Node
from agents.prompts.prompt import prompt_afther_data_query
from langchain.chains.llm import LLMChain
import sys
sys.path.append('../')
from tools.dataManager import generate_and_execute_query

class DataNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name, askfoinfo):
        super().__init__(llm, children, prompt, name)
        self.askforinfo = askfoinfo
        

    def call_chain(self, input_dict):
        response = self.chain.invoke(input_dict)
        print(response)
        response = response['text']
        #last_interaction = [input_dict['chat_history'][-2] ,input_dict['chat_history'][-1]]
        #input = f'{last_interaction[0]} {last_interaction[1]} data: {self.askforinfo.user_details}'
        resposta = generate_and_execute_query(response)
        
        afther_chain = LLMChain(prompt=prompt_afther_data_query, llm=self.llm)
        input_dict['input'] = resposta
        response = afther_chain.invoke(input_dict)
        print(response)
        return response