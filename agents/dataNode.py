from agents.node import Node
import sys
sys.path.append('../')
from tools.dataManager import execute

class DataNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name, askfoinfo):
        super().__init__(llm, children, prompt, name)
        self.askforinfo = askfoinfo
        

    def call_chain(self, input_dict):
        last_interaction = [input_dict['chat_history'][-2] ,input_dict['chat_history'][-1]]
        input = f'{last_interaction[0]} {last_interaction[1]} data: {self.askforinfo.user_details}'
        return {'text' :execute(input)}