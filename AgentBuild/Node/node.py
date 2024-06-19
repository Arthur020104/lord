from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
class Node():
    def __init__(self, llm, children: dict[str, 'Node'], prompt: ChatPromptTemplate, name:str,property_info_key:[str] = []):
        self.llm = llm
        self.name = name
        self.children = children
        self.prompt = prompt
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.property_info_key = property_info_key
    def add_child(self, key, value):
        self.children[key] = value
    def get_children(self):
        return self.children
    def call_chain(self, dict_input:dict):
        return {'text':self.chain.invoke(dict_input)}
    def get_name(self):
        return self.name
    def filter_property_info(self, property_info):
        if not self.property_info_key:
            return property_info
        elif len(self.property_info_key) == 1:
            return {self.property_info_key[0]:property_info[self.property_info_key[0]]}
        else:
            return {key:property_info[key] for key in self.property_info_key}
    def process_input(self,input_last_interaction):
        pass
    
    