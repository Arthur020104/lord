from langchain_core.prompts import ChatPromptTemplate  # Importa o template de prompts do LangChain
from langchain.schema.output_parser import StrOutputParser  # Importa o parser de saída que converte para string

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

    def call_chain(self, dict_input: dict):
        # Chama a cadeia de processamento com o dicionário de entrada e retorna o resultado como texto
        return {'text': self.chain.invoke(dict_input)}

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
