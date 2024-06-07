from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
class Node():
    def __init__(self, llm, children: dict[str, 'Node'], prompt: ChatPromptTemplate, name:str):
        self.llm = llm
        self.name = name
        self.children = children
        self.prompt = prompt
        self.chain = LLMChain(prompt=self.prompt,llm=llm)
    def add_child(self, key, value):
        self.children[key] = value
    def get_children(self):
        return self.children
    def call_chain(self, dict_input:dict):
        return self.chain.invoke(dict_input)
    def get_name(self):
        return self.name
    def process_input(self,input_last_interaction):
        pass
    
    