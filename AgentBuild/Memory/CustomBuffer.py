
class CustomConversationTokenBufferMemory:
    def __init__(self, ia_key = "output", human_key = "input", max_token_limit = 200,order = 0):
        self._ia_key = ia_key
        self._human_key = human_key
        self._max_token_limit = max_token_limit
        self._chat_memory = []
        self._order = order
    def add(self, human_input, ia_output):
        if self._order == 0:
            self._chat_memory.append({self._ia_key: ia_output, self._human_key: human_input})
        else:
            self._chat_memory.append({self._ia_key: ia_output, self._human_key: human_input})
       # self._chat_memory.append({self._human_key: human_input, self._ia_key+str(self._ia_output_count): ia_output})
        self.clear()
    def _count_tokens(self):
        estimate_tokens = 0
        count = 0
        for interaction in self._chat_memory:
            human_tokens = len(interaction[self._human_key].split())
            ia_tokens = len(interaction[self._ia_key].split())
            count += 1
        
            estimate_tokens += human_tokens + ia_tokens
        estimate_tokens = int(estimate_tokens * 1.25)
        return estimate_tokens

    def clear(self):
        while self._count_tokens() > self._max_token_limit:
            self._chat_memory.pop(0)
    def get_memory(self):
        return self._chat_memory
    def get_memory_tuple(self):
        full_memory = []
        for conversation in self._chat_memory:
           # conver = []
            tuple_ia = (self._ia_key, conversation[self._ia_key])
            tuple_human = (self._human_key, conversation[self._human_key])
            full_memory.append(tuple_ia)
            full_memory.append(tuple_human)
            #full_memory.append(conver)
        return full_memory
    def delete_memory(self):
        self._chat_memory = []
            
    