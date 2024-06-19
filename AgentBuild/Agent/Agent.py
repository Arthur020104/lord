from AgentBuild.Node.node import Node
from AgentBuild.Memory.CustomBuffer import CustomConversationTokenBufferMemory
from langchain_core.runnables.base import RunnableSequence
import json
class Agent:
    def __init__(self,initial_node:Node, all_nodes:dict, memory:CustomConversationTokenBufferMemory,agent_info:dict, manager:RunnableSequence, nodes_info:dict):
        self.node = initial_node
        self.initial_node = initial_node
        self.all_nodes = all_nodes
        self.memory = memory
        self.agent_info = agent_info
        self.manager = manager
        self.last_output = ""
        self.nodes_info = nodes_info
        # Add children to nodes
        for node_name, cnode in self.all_nodes.items():
            for child_name, child_node in all_nodes.items():
                cnode.add_child(child_name, child_node)


    def call_current_node(self):
        try:
            print(f"Current node: {self.node.get_name()}")
            self.nodes_info['chat_history'] = self.memory.get_memory_tuple()
            self.nodes_info['property_info'] = self.node.filter_property_info(self.agent_info)
            response = self.node.call_chain(self.nodes_info)
            self.last_output = response['text']
            return response
        except Exception as e:
            print(f"Error in call_current_node: {e}")
            return {"text": "An error occurred. Please try again later."}

    def process_user_input(self,user_input):
        try:
            self.memory.add(human_input=user_input, ia_output=self.last_output)
            self.node.process_input(self.memory.get_memory()[-1])
            
            self.nodes_info['chat_history'] = self.memory.get_memory_tuple()
            for _ in range(3):
                try:
                    node_called = self.manager.invoke({
                        'chat_history': self.memory.get_memory_tuple(),
                        'nodes': list(self.node.get_children().keys()),
                        'current_node': self.node.get_name()
                    })
                    data_dict = node_called
                    node_called = data_dict['node']
                    print(f"Node called: {node_called}, why called: {data_dict['answer']}")
                    if node_called != "Não existe":
                        self.node = self.node.get_children()[node_called]
                    break
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except KeyError as e:
                    print(f"Key error: {e}")
        except Exception as e:
            print(f"Error in process_user_input: {e}")

    def delete_memory(self):
        self.memory.delete_memory()
        self.node = self.initial_node
        print("Memory deleted and conversation reset to initial node.")

