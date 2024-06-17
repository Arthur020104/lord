import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from agents.main import call_current_node, process_user_input

# Todo: Descobrir algum jeito de falar com varios ameegans, testar multithreading primeiro, em ultimo caso testar um aws
# pq nao quero mexer com aws

def setup_whatsapp():
    driver = webdriver.Chrome()  # Utilizando Chrome
    driver.get("https://web.whatsapp.com")

    # Espera o usuário escanear o QR Code e apertar Enter
    input("Pressione Enter após escanear o QR Code e carregar o WhatsApp Web...")
    time.sleep(5)

    return driver

def start_new_conversation(driver, contact_number):
    # Aqui eu procuro o botao de nova conversa
    new_chat_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@title="Nova conversa"]'))
    )
    #Clico nele
    new_chat_button.click()
    
    # Procuro a caixa de inserir contato
    contact_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
    )
    contact_input.click()
    # Clico nela
    contact_input.send_keys(contact_number) # Sei la se esses sleeps sao necessários, mas vai que a pagina demora carregar.
    time.sleep(1)
    contact_input.send_keys(Keys.ENTER)
    time.sleep(2)

def read_last_message(driver):
    try:
        # Pego mensagens que estão vindo...
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
        all_messages = []
        for message in messages:
            try:
                message_type = message.get_attribute("class")
                if "message-in" in message_type:  # Só pego mensagens que chegam
                    text = message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]/span').text
                    all_messages.append(text)  # Coloco tudo em all_messages
            except Exception as e:
                continue
        
        if all_messages:
            new_message = all_messages[-1]  # Pego a última mensagem
            print(f"New_Message: {new_message}") 
            print(all_messages)  # Printo todas as mensagens só para ver como funciona...

            # Contar quantas vezes a nova mensagem é repetida consecutivamente no final da lista
            consecutive_count = 0
            for msg in reversed(all_messages[:-1]):
                if msg == new_message:
                    consecutive_count += 1
                else:
                    break
            
            if consecutive_count > 0:
                new_message += '!' * consecutive_count 
                # Pra que serve: Ele checa se a mensagem é igual para ver se uma mensagem
                # nova é adicionada, porém, é possivel que o usuario digite sim, sim, e sejam mensagens diferentes, então se
                # as mensagens forem consecutivas e no final eu vou adicionando ! para diferenciar elas, é gambiarra mas funciona ok!
            return new_message
        return None
    except Exception as e:
        print(f"Error reading last message: {e}")
        return None
    

def send_message(driver, message):
    try:
        message_box = WebDriverWait(driver, 30).until(
            # Clicar no chat pra enviar mensagem
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.click()
        message_box.send_keys(message) # Mandar a mensagem que vem da LLM
        time.sleep(0.5)
        message_box.send_keys(Keys.ENTER) # Aperta Enter pra enviar
    except Exception as e:
        print(f"Error sending message: {e}")

def save_conversation(user_input, response, phone_number, data_resposta_user):
    # Cria a pasta 'conversas' se ela não existir
    if not os.path.exists('conversas'):
        os.makedirs('conversas')

    # Define o nome do arquivo como o número de telefone
    filename = os.path.join('conversas', f'{phone_number}.json')

    # Carrega o JSON existente ou cria um novo se não existir
    try:
        with open(filename, 'r') as file:
            conversas = json.load(file)
    except FileNotFoundError:
        conversas = []

    # Formata a conversa atual
    data_hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conversa_atual = {
        "User - Data e horario atual": data_resposta_user,
        "User input": user_input,
        "Lord - Data e horario atual": data_hora_atual,
        "Response": response
    }

    # Adiciona a conversa atual à lista de conversas
    conversas.append(conversa_atual)

    # Salva a lista de conversas de volta no arquivo JSON
    with open(filename, 'w') as file:
        json.dump(conversas, file, ensure_ascii=False, indent=4)


# O que isso faz: A função main_loop() roda até ctrl+c ser ativado ou um erro acontecer, ela entra no whatsapp_web
# espera a confirmação do QR code, e então você tem que dar enter no console, ela vai digitar o numero do contact
# na caixa de busca e então apertar enter, ela faz uma chamada para a LLM, e manda a resposta inicial, então
# coloca as mensagens em uma lista, e pega apenas a ultima para mandar para a LLM e ir resolvendo essa bomba.

def main_loop(phone_number):
    driver = setup_whatsapp()
    start_new_conversation(driver, phone_number)

    # Inicializa a última mensagem com a mensagem mais recente da conversa, essa bomba aqui é pra não pegarmos mensagens
    # antigas...
    last_message = read_last_message(driver)
    print(f"Última mensagem inicializada como: {last_message}") # Printando aqui so pra deixar claro o que ta rolando

    response = call_current_node()['text'] # Transformando o dicionario em string
    send_message(driver, response) # Mandando a primeira mensagem da LLM, da startconversationchain...

    try:
        while True:
            # Ler a última mensagem
            user_input = read_last_message(driver)
            if user_input and user_input != last_message: 

                # Vendo o input que vem da messagem
                print(f"O input para ser processado foi: {user_input}")
                data_resposta_user = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Hora que usuario respondeu
                last_message = user_input # last_message vai pegar o valor de user input pra comparar se existem mensagens
                # novas
                process_user_input(user_input) # Manda pra LLM

                # Chama a resposta denovo
                response = call_current_node()['text'] # Pega da LLM
                send_message(driver, response) # Envia pro zipzoper

                # Salva a conversa no arquivo JSON
                save_conversation(user_input, response, phone_number, data_resposta_user) # Salvando no Json
            
            time.sleep(1)  # Aguarda 1 segundo antes de verificar novamente
    except KeyboardInterrupt:
        print("Chat interaction stopped.") # Usa Ctrl + C pra cancelar interação do bot
    finally:
        driver.quit() # Tenho menor ideia do que isso faz

if __name__ == "__main__":
    main_loop(phone_number = "553492631397") # Setando o numero de telefone