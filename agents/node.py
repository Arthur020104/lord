from langchain.chains.llm import LLMChain
from langchain.schema.output_parser import StrOutputParser
from agents.prompts.string_prompts import prompt_for_review, prompt_for_final_answer, basic_prompt
class Node():
    def __init__(self, llm, children: dict[str, 'Node'], prompt:str, name):
        self.llm = llm
        self.name = name
        self.children = children
        self.prompt = prompt
        self.chain = LLMChain(prompt=basic_prompt,llm=llm)
    def add_child(self, key, value):
        self.children[key] = value
    def get_children(self):
        return self.children
    def call_chain(self, dict_input:dict, cycles:int = 1):
        dict_input['system_prompt'] = self.prompt
        question = self.chain.invoke(dict_input)['text']
        for i in range(cycles):
            question = Node.improvement_cycle(self.llm, question, dict_input['chat_history'], system_prompt=self.prompt)
        
        return {'text': question}
    def get_name(self):
        return self.name
    def process_input(self,input_last_interaction):
        pass
    @staticmethod
    def improvement_cycle(llm, inicial_answer, chat_history, system_prompt):
        review_chain =  prompt_for_review | llm | StrOutputParser()
        constructive_criticism = review_chain.invoke({'question': inicial_answer, 'chat_history': chat_history, 'system_prompt': system_prompt})
        print(constructive_criticism)
        
        final_chain = prompt_for_final_answer | llm | StrOutputParser()
        final_result = final_chain.invoke({
            'system_prompt': system_prompt,
            'question': inicial_answer,
            'constructive_criticism': constructive_criticism,
            'chat_history': chat_history
        })
        return final_result
    
    