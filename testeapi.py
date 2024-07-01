import requests

BASE_URL = "http://127.0.0.1:5000"

def start_conversation():
    response = requests.post(f"{BASE_URL}/start_conversation")
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"Conversation started. Token: {token}")
        return token
    else:
        print(f"Failed to start conversation: {response.text}")
        return None

def call_current_node(token):
    headers = {'Authorization': token}
    response = requests.post(f"{BASE_URL}/call_current_node", headers=headers)
    if response.status_code == 200:
        print(f"Current node response: {response.json()}")
    else:
        print(f"Failed to call current node: {response.text}")

def process_user_input(token, user_input):
    headers = {'Authorization': token}
    response = requests.post(f"{BASE_URL}/process_user_input", headers=headers, data=user_input)
    if response.status_code == 200:
        print(f"User input processed successfully")
    else:
        print(f"Failed to process user input: {response.text}")

def reset_memory(token):
    headers = {'Authorization': token}
    response = requests.post(f"{BASE_URL}/reset_memory", headers=headers)
    if response.status_code == 200:
        print("Memory reset successfully")
    else:
        print(f"Failed to reset memory: {response.text}")

if __name__ == "__main__":
    # Iniciar uma nova conversa e obter um token
    token = start_conversation()
    if token:
        # Chamar o nó atual do agente
        call_current_node(token)
        # Enviar uma entrada do usuário e obter resposta do agente
        user_input = "Olá, eu gostaria de saber mais sobre os apartamentos disponíveis."
        # Processar a entrada do usuário
        process_user_input(token, user_input)
        # Reiniciar a memória do agente
        reset_memory(token)
