import requests
import json


# Nesse Script colocamos o telefone que será utilizado no lordChat
# URL do endpoint no servidor Flask
url = "http://192.168.15.7:5000/start_chat"

# Payload (dados) da requisição - o número de telefone que será enviado
payload = {
    "phone_number": "+55 34 9672 4123"
}

# Cabeçalhos da requisição - especificando que o conteúdo é do tipo JSON
headers = {
    "Content-Type": "application/json"
}

# Função para enviar a requisição POST
def send_post_request(url, payload, headers):
    try:
        # Envia a requisição POST
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        # Verifica se a resposta do servidor é bem-sucedida (código 200)
        if response.status_code == 200:
            print("Requisição enviada com sucesso!")
            print("Resposta do servidor:", response.json())
        else:
            print(f"Erro na requisição: {response.status_code}")
            print("Mensagem de erro:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

# Envia a requisição POST com o número de telefone
send_post_request(url, payload, headers)
