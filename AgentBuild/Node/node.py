from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # Importa o template de prompts do LangChain
from langchain.schema.output_parser import StrOutputParser  # Importa o parser de saída que converte para string
import copy
class Node():
    def __init__(self, llm, children: dict[str, 'Node'], prompt: ChatPromptTemplate, name: str, property_info_key: list[str] = []):
        self.llm = llm  # Modelo de linguagem usado pelo nó
        self.name = name  # Nome do nó
        self.children = children  # Filhos do nó (outros nós)
        self.prompt = prompt  # Template do prompt usado para interações
        self.chain = self.prompt | self.llm | StrOutputParser()  # Cadeia de processamento do nó: prompt -> modelo de linguagem -> parser de string
        self.property_info_key = property_info_key  # Chaves específicas para filtrar informações de propriedades

    def add_child(self, key, value): # Nao utilizamos essas duas, for now
        # Adiciona um nó filho ao nó atual
        self.children[key] = value

    def get_children(self):
        # Retorna os filhos do nó atual
        return self.children

    def call_chain(self, dict_input: dict,cycle=2, improvement_cycle=False):
        # Chama a cadeia de processamento com o dicionário de entrada e retorna o resultado como texto
        inicial_answer = self.chain.invoke(dict_input)
        if improvement_cycle:
            for _ in range(cycle):
                inicial_answer = self.improvement_cycle(self.llm, inicial_answer, dict_input['chat_history'],dict_input)
        return {'text': inicial_answer}

    def get_name(self):
        # Retorna o nome do nó
        return self.name

    def filter_property_info(self, property_info):
        # Se não houver chaves específicas, retorna todas as informações
        if not self.property_info_key:
            return property_info

        # Retorna as informações filtradas com base nas chaves especificadas
        return {key: property_info[key] for key in self.property_info_key if key in property_info}

    def process_input(self, input_last_interaction):
        # Se precisar ta aqui, mas tem que implementar - Arthur
        pass
    def improvement_cycle(self,llm, inicial_answer, chat_history,information):
        prompt_for_review = ChatPromptTemplate.from_messages([
            MessagesPlaceholder("chat_history"),
            ('system', """{system_prompt}You are a helpful assistant that reviews answers and critiques based on the original question given and the conversations guidelines. The information you have is this {information}"""),#Using + instead of f string because langchain uses {} to replace the placeholders
            ('user', "### Your Generated Question: \n\n {question} \n\n ### Review your previous question and find problems with your question. Generate constructive criticism based on the problems you found. \n\n ### Constructive Criticism:"),
        ])

        prompt_for_final_answer = ChatPromptTemplate.from_messages([
            MessagesPlaceholder("chat_history"),
            ('system', """{system_prompt}You are a helpful assistant who writes an improved final answer based on the constructive review and the conversation guidelines. Using this conversations guidelines and the constructive review improve the inicial answer. The information you have is this {information}"""),#Using + instead of f string because langchain uses {} to replace the placeholders
            ('user', """### Generated Question: \n\n {question} \n\n ### Review your previous question and find problems with your question.\n\n ###Constructive Criticism:{constructive_criticism}\n\n Based on the problems you found, improve your question.\n\n  Make it cooherent with the conversation history. {chat_history}.
                        This is a conversation so you should ask for the information in a conversational way(never ask for more than one piece of information at a time). \n\n### Final question:"""),
        ])
        review_chain =  prompt_for_review | llm | StrOutputParser()
        constructive_criticism = review_chain.invoke({'question': inicial_answer, 'chat_history': chat_history, 'system_prompt': copy.copy(self.prompt), 'information':information})
        print(constructive_criticism)
        final_chain = prompt_for_final_answer | llm | StrOutputParser()
        final_result = final_chain.invoke({
            'system_prompt': copy.copy(self.prompt),
            'question': inicial_answer,
            'constructive_criticism': constructive_criticism,
            'chat_history': chat_history,
            'information':information
        })
        return final_result
