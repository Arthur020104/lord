from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Definição da classe Prompt
class Prompt:
    def __init__(self):
        self.prompt = ChatPromptTemplate
        self.messages = []
        
    def add_message(self, messager: str, message: str):
        message = (messager, message)
        self.messages.append(message)
        
    def set_messages(self, messages: list[tuple[str, str]]):
        if all(isinstance(message, tuple) and len(message) == 2 and all(isinstance(item, str) for item in message) for message in messages):
            self.messages = messages
        else:
            raise ValueError("messages should be a list of tuples, each containing exactly two strings")
        
    def get_prompt(self):
        return self.prompt.from_messages(self.messages)
    
    def set_history_key(self, history:str):
        if not isinstance(history, str):
            raise ValueError("history should be a str object")
        self.messages.append(MessagesPlaceholder(history))

