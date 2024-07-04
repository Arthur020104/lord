from AgentBuild.Node.node import Node
from AgentBuild.Memory.CustomBuffer import CustomConversationTokenBufferMemory
from langchain_core.runnables.base import RunnableSequence
from langchain_community.callbacks import get_openai_callback
import json
class Agent:
    def __init__(self,initial_node:Node, all_nodes:dict, memory:CustomConversationTokenBufferMemory,agent_info:dict, manager:RunnableSequence, nodes_info:dict, verbose_prices = False):
        self.node = initial_node # Ponto de partida / No inicial
        self.initial_node = initial_node  # ??? Acho que isso é redundante
        self.all_nodes = all_nodes # Todos os nós que o agente pode suar
        self.memory = memory # Guarda memorias de conversas passadas
        self.agent_info = agent_info # Informações do agente / Nao sei exatamente o que é isso
        self.manager = manager # Manager, ou router que vai gerir e guiar os nós.
        self.last_output = "" # Ultima resposta 
        self.nodes_info = nodes_info # Informação especifica de cada nó
        self.verbose_prices = verbose_prices # Se vai mostrar os preços ou não
        # Fazendo todo mundo se ligar
        for node_name, cnode in self.all_nodes.items():
            for child_name, child_node in all_nodes.items():
                cnode.add_child(child_name, child_node)


    def call_current_node(self):
        try:
            if self.verbose_prices and not self.node.verbose_prices:
                self.node.toggle_verbose_prices()
            print(f"Current node: {self.node.get_name()}") # Mostra o nó atual
            self.nodes_info['chat_history'] = self.memory.get_memory_tuple() # Atualiza historico
            self.nodes_info['property_info'] = self.node.filter_property_info(self.agent_info) # Filtra as informações do property_info
            response = self.node.call_chain(self.nodes_info) # Chama a funcao de resposta do nó atual
            self.last_output = response['text'] # Transforma isso em texto e retorna
            return response
        except Exception as e:
            print(f"Error in call_current_node: {e}")
            return {"text": "An error occurred. Please try again later."}

    def process_user_input(self,user_input):
        try:
            # Pega ultimo input do usuario e a ultima resposta que está na memoria
            self.memory.add(human_input=user_input, ia_output=self.last_output)
            # Processa o input no nó atual
            self.node.process_input(self.memory.get_memory()[-1])
            
            self.nodes_info['chat_history'] = self.memory.get_memory_tuple() # Atualiza o histórico de chat

            for _ in range(3): # Tenta no máximo 3 vezes, nao sei pq isso ta aqui mas tá
                try:
                    # tenta chamar o próximo nó que o manager decidir
                    with get_openai_callback() as cb:
                        node_called = self.manager.invoke({
                            'chat_history': self.memory.get_memory_tuple(),
                            'nodes': list(self.node.get_children().keys()),
                            'current_node': self.node.get_name()
                        })
                    if self.verbose_prices:
                        print(f"\nUso do manager\nTotal Tokens: {cb.total_tokens}")
                        print(f"Prompt Tokens: {cb.prompt_tokens}")
                        print(f"Completion Tokens: {cb.completion_tokens}")
                        print(f"Total Cost (USD): ${cb.total_cost}\n")
                    data_dict = node_called
                    node_called = data_dict['node'] # proximo nó chamado
                    print(f"Node called: {node_called}, why called: {data_dict['answer']}") # Por que chamou o proximo nó
                    if node_called != "Não existe": # Se achou nó valido
                        self.node = self.node.get_children()[node_called] # muda para o nó válido
                    break
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except KeyError as e:
                    print(f"Key error: {e}")
        except Exception as e:
            print(f"Error in process_user_input: {e}")

    def delete_memory(self): # Apaga as memorias e volta para nó inicial
        self.memory.delete_memory() 
        self.node = self.initial_node
        print("Memory deleted and conversation reset to initial node.")
    def get_current_node(self):
        return self.node.get_name()

