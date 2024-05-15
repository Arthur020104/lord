from langchain.chains.llm import LLMChain
from langchain.chains.openai_functions.tagging import create_tagging_chain_pydantic
from langchain_core.prompts import ChatPromptTemplate
from memory.PropertyDetails import PropertyDetails
from agents.askForInfo import ask_for_info
from agents.node import Node
class AskForInfoNode(Node):
    def __init__(self, llm, children: dict[str, Node], prompt,name):
        self.user_details = PropertyDetails()
        super().__init__(llm, children, prompt, name)

    def add_non_empty_fields(self, current_details, new_details):
        non_empty_details = {k: v for k, v in new_details.dict().items() if v not in [None, "", 0]}
        for k, v in current_details.dict().items():
            if v not in [None, "", 0]:
                non_empty_details[k] = v
        updated_details = current_details.copy(update=non_empty_details)
        return updated_details

    def check_what_is_missing(self, input):
        ask_for = []
        for field, value in input.dict().items():
            if value in [None, "", 0]:
                ask_for.append(field)
        return ask_for

    def filter_response(self, question, text_input):
        prompt = ChatPromptTemplate.from_messages([
            ('system', """
                You are responsible for filling in the `PropertyDetails` class with the user's preferences for a property.

                The fields are as follows:

                - **City**: str
                - The city where the person wants to live.

                - **Property Type**: str
                - Options: 'house', 'apartment', 'condominium'.
                - The type of property that the person wants to live in.

                - **Number of Rooms**: int
                - The number of rooms that the person wants in the property.

                - **Number of Bathrooms**: int
                - The number of bathrooms that the person wants in the property.

                - **Number of Suites**: int
                - The number of suites that the person wants in the property.

                - **Amenities**: List[str]
                - The amenities that the person wants in the property or condominium if it is one.

                - **Location Neighborhood**: str
                - The neighborhood where the person wants to live.

                - **Number of Parking Spaces**: int
                - The number of parking spaces that the person wants in the property.

                - **Price Range Lower**: int
                - The lower limit of the price range. If only one value is provided, lower is equal to (base_price - 10%).

                - **Price Range Upper**: int
                - The upper limit of the price range. If only one value is provided, upper is equal to (base_price + 10%).

                - **User explicit say that he wants to search for property**: bool
                - If the user wants to search for a property, they must explicitly say so. If the search is not explicit, the agent should assume that it is false.

                Please ensure that each field is filled accurately according to the user's preferences.
            """),
            ('user', 'Interaction: ai: {ai} user: {user}'),
        ])
        input_ia = f'question: {question} answer: {text_input}'
        chain = create_tagging_chain_pydantic(pydantic_schema=PropertyDetails, llm=self.llm, prompt=prompt)
        
        res = chain.invoke({'ai': question, 'user': text_input})['text']
        input_ia = f'question: {input_ia} answer: {res}'
        
        res = self.add_non_empty_fields(self.user_details, res)
        ask_for = self.check_what_is_missing(res)
        return res, ask_for
    def process_input(self, input_last_interaction):
        self.filter_response(input_last_interaction['ai'], input_last_interaction['human'])
#this is not working yet fix for processing user input
    def call_chain(self, dict_input: dict):
        missing_info = self.check_what_is_missing(self.user_details)
        if missing_info:
            question = ask_for_info([missing_info], dict_input['chat_history'])
            return question
          #  self.user_details, missing_info = self.filter_response(question, user_response, self.user_details)
        #return self.user_details