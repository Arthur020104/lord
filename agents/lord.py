from langchain_openai import ChatOpenAI
from langchain.chains.openai_functions.tagging import create_tagging_chain_pydantic
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, MessagesPlaceholder
from memory.PropertyDetails import PropertyDetails
from memory.UserInterested import UserInterested
from memory.CustomBuffer import CustomConversationTokenBufferMemory
from agents.askForInfo import ask_for_info
import sys
from tools.dataManager import execute

sys.path.append('../')
from secret.apiOpenAI import api_key
llm = ChatOpenAI(api_key=api_key, temperature=0.0, model="gpt-3.5-turbo")

def check_what_is_missing(input):
    ask_for = []
    for field, value in input.dict().items():
        if value in [None, "", 0]:
            ask_for.append(field)
    return ask_for

def add_non_empty_fields(current_details, new_details):
    non_empty_details = {k: v for k, v in new_details.dict().items() if v not in [None, "", 0]}
    
    for k, v in current_details.dict().items():
        if v not in [None, "", 0]:
            non_empty_details[k] = v
    updated_details = current_details.copy(update=non_empty_details)
    return updated_details

memory = CustomConversationTokenBufferMemory(max_token_limit=2000, ia_key="ai", human_key="human", order=1)

def inicial_chat(chat_history=[], nome_do_cliente='Arthur', nome_da_imobiliaria='ginga imoveis', last_interaction=''):
    property_info = {"UnitType": "CONDOMINIUM", "ListingType": "USED", "State": "Minas Gerais", "City": "Uberlândia", "Neighborhood": "Jardim Karaíba", "Street": "Avenida Vereador Junior de Oliveira", "ZipCode": 38410665, "Title": "Casa Nova a Venda no Condomínio Dois Irmãos", "Price": 1700000, "CondominiumFee": 590.0, "UsableAreas": 206, "Bedrooms": 3, "Bathrooms": 2, "Suites": 3.0, "ParkingSpaces": 4.0}
    if chat_history == None:
        chat_history = []
    start_conversation = ""
    if len(chat_history) == 0:
        start_conversation = """Use this example to start the conversation:
        "Olá, [Nome do Cliente], meu nome é [Seu Nome], e estou ligando da [Nome da Imobiliária]. Desculpe interromper seu dia. Pode me conceder um minuto para discutir algo que pode ser muito vantajoso para você?"
        Make sure to replace the placeholders with the correct information."""
    prompt = ChatPromptTemplate.from_messages([
        ('system', '\nproperty_info this is the only information about the property: {property_info}'),
        ('system', 'client_name: {nome_do_cliente}'),
        ('system', 'agency_name: {nome_da_imobiliaria}'),
        ('system', 'agent_name: Lord GPT'),
        MessagesPlaceholder("chat_history"),
      #  ('system', """Last Interaction: {last_interaction}"""),
        ('system', f"""
        ###
        You are a helpful real estate agent trying to sell a specific property to a user. And you have conversations gui
        Conversation Reference:
        conversation guidelines:
        Language: pt-BR
        1. Start the conversation respectfully and introduce yourself as a real estate agent.
        2. Share property information gradually and ask for feedback.
        3. If the user declines or is busy, offer alternative times or methods of communication.
        4. Ask about their preferences if they decline the property.
        5. If the user wants to end the conversation, ask for recommendations or referrals.
        6. Keep the conversation conversational and never show all property information at once show around 2 to 3 features at a time.
        7. Always follow the introduction and conversation references.
        8. Avoid repeating greetings and thank the user politely at the end of the conversation.
        9. Never show all property information at once, principally in the start of the conversation.
        10. If user tells you that have no time to talk or is busy, offer alternative times or methods of communication. If you re-arrenge the conversation or a new form of communication, tanks the user for the time and say that you will happly wait and end the conversation.
        11. When conversation is re-arranged, finish the conversation with a polite thank you and say that you will be waiting for the user, never ask something in a farewell.
        12. Never assume information about the property or the user, use the information provided.
        13. If you don't know a specific information about the property tell the user that you dont have that information.
        14.Don't use words such as 'usually', 'normally', 'most likely', 'tipically', 'generally', 'probably', 'possibly', 'perhaps', 'maybe', 'might', 'could', 'can', 'should', 'would' or 'will'
        ###
        Do not give me any information about procedures and service features that are not mentioned in the PROVIDED CONTEXT.
        Is very important to follow the conversation guidelines and the conversation references.
        Do not give any infomation about the property that is not in the provided context.
        IS very important to not give any information about the property that is not in the provided context.
        
        {start_conversation}
        """),
    ])
    print(f'Current chat history: {chat_history}')
    llm = ChatOpenAI(api_key=api_key, temperature=0.0, model="gpt-3.5-turbo")
    inicial_chat_chain =LLMChain(prompt=prompt,llm=llm) #prompt | llm2
    
    
    ai_chat = inicial_chat_chain.invoke({'chat_history': chat_history, 'nome_do_cliente': nome_do_cliente, 'nome_da_imobiliaria': nome_da_imobiliaria, 'property_info': property_info,'last_interaction': last_interaction})
    print(ai_chat)
    return ai_chat

def tell_if_user_is_interested(ai_, input, chat_history, user_interested):
    #prompt_str = f'\nConversation history: {chat_history}\n \n ai:{ai_} \n \n User:{input} \n'
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ('system', """
         You are an agent responsible for filling the UserInterested class with the information that the user is interested in.
         The fields are:
            -  inicial_conversation_is_over: bool
              This field must be filled to indicate whether the initial conversation with the user has concluded because they are interested in another property. For example, if the user expresses a preference for a property with specific features that differ from the proposed property, such as 'Não gostei, gostaria de um imóvel com 3 banheiros,' then this field would have a True value. It should only be true when the user is interested in another property or after the agent has finished speaking about the property they are offering
            - is_interested_in_another_property: bool
                This field must be filled to indicate whether the user is interested in a property other than the one initially proposed. For example, if the user expresses interest in a property with different characteristics than the proposed one, such as 'Não gostei, gostaria de um imóvel com 3 banheiros,' this field should also have a True value. It should be set to True when the user is requesting information or expressing interest in a property with different characteristics than the one initially proposed. An example of this is the phrase 'Não gostei, gostaria de no mínimo 4 quartos.'
         """),
        ('user', 'Interaction: ai: {ai} user: {user}'),
    ])
    llm2 = ChatOpenAI(api_key=api_key, temperature=0.0, model="gpt-3.5-turbo")
    chain = create_tagging_chain_pydantic(pydantic_schema=UserInterested, llm=llm2,prompt=prompt)
    
    res = chain.invoke({'chat_history': chat_history, 'ai': ai_, 'user': input})
    res = res['text']
    print(res)
    
    res = add_non_empty_fields(user_interested, res)
    return res

def filter_response(question, text_input, user_details):
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
    chain = create_tagging_chain_pydantic(pydantic_schema=PropertyDetails, llm=llm,prompt=prompt)
    
    res = chain.invoke({'ai':question,'user':text_input})['text']
    input_ia = f'question: {input_ia} answer: {res}'
    
    res = add_non_empty_fields(user_details, res)
    ask_for = check_what_is_missing(res)
    return res, ask_for

global ask_for, last_question, user_details, inicial_chat_over, user_interested, user_interested_in_another_property

user_interested_in_another_property = False
user_interested = UserInterested()
inicial_chat_over = False
last_question = {'text':''}
user_details = PropertyDetails()

def get_user_info():
    global user_details
    return user_details

def generate_question():
    global ask_for, last_question, inicial_chat_over, user_interested_in_another_property

    if user_interested_in_another_property:
        if not ask_for or get_user_info().user_wants_to_search_for_property:
            return {'text': execute(get_user_info())}
        last_question = ask_for_info(ask_for, memory.get_memory_tuple())
        return last_question
    last_question = inicial_chat(chat_history=memory.get_memory_tuple())
    return last_question

def get_user_input(input):
    global ask_for, user_details, last_question, inicial_chat_over, user_interested, user_interested_in_another_property
    
    print(f'\n\n Adding to memory: Human: {input} \n IA: {last_question} \n\n')
    memory.add(human_input=input, ia_output=last_question['text'])
    
    if inicial_chat_over and user_interested_in_another_property:
        user_details, ask_for = filter_response(last_question["text"], input, user_details)
    elif not inicial_chat_over:
       # conversation_memory = memory.get_memory()
       # last_interaction = conversation_memory[len(conversation_memory)-1] if len(conversation_memory) > 0 else {}
        user_interested = tell_if_user_is_interested(last_question["text"], input, memory.get_memory_tuple(), user_interested)
        
        inicial_chat_over = user_interested.inicial_conversation_is_over
        user_interested_in_another_property = user_interested.is_interested_in_another_property
        
        if inicial_chat_over:
            user_details, ask_for = filter_response(last_question["text"], input, user_details)
    return UserInterested(), ['Tetse']