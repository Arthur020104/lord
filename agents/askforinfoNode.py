from langchain.chains.openai_functions.tagging import create_tagging_chain_pydantic
from memory.PropertyDetails import PropertyDetails
from agents.askForInfo import ask_for_info
from agents.prompts.askforinfo_prompts import prompt_filter_response
from agents.node import Node

class AskForInfoNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt, name):
        super().__init__(llm, children, prompt, name)
        self.user_details = PropertyDetails()

    def add_non_empty_fields(self, current_details, new_details):
        non_empty_details = {k: v for k, v in new_details.dict().items() if v not in [None, "", 0]}
        for k, v in current_details.dict().items():
            if v not in [None, "", 0]:
                non_empty_details[k] = v
        updated_details = current_details.copy(update=non_empty_details)
        return updated_details

    def check_what_is_missing(self, input):
        ask_for = [field for field, value in input.dict().items() if value in [None, "", 0]]
        return ask_for

    def filter_response(self, question, text_input):
        input_ia = f'question: {question} answer: {text_input}'
        chain = create_tagging_chain_pydantic(pydantic_schema=PropertyDetails, llm=self.llm, prompt=prompt_filter_response)
        res = chain.invoke({'ai': question, 'user': text_input})['text']
        input_ia = f'question: {input_ia} answer: {res}'
        res = self.add_non_empty_fields(self.user_details, res)
        ask_for = self.check_what_is_missing(res)
        return res, ask_for

    def process_input(self, input_last_interaction):
        self.filter_response(input_last_interaction['ai'], input_last_interaction['human'])

    def call_chain(self, dict_input: dict):
        missing_info = self.check_what_is_missing(self.user_details)
        if missing_info:
            question = ask_for_info([missing_info], dict_input['chat_history'])
            return question
