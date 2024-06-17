import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from agents.main import call_current_node, process_user_input

def setup_whatsapp():
    driver = webdriver.Chrome()  # Utilizando Chrome
    driver.get("https://web.whatsapp.com")

    # Espera o usuário escanear o QR Code
    input("Pressione Enter após escanear o QR Code e carregar o WhatsApp Web...")
    time.sleep(10)

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
    contact_input.send_keys(contact_number)
    time.sleep(1)
    contact_input.send_keys(Keys.ENTER)
    time.sleep(2)

def read_last_message(driver): # Tenho que mexer nesses try e exception, perhaps.
    try:
        # Pego mensagens que estao vindo...
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
        all_messages = []
        for message in messages:
            try:
                message_type = message.get_attribute("class")
                if "message-in" in message_type:  # So pego mensagens que chegam
                    text = message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]/span').text
                    all_messages.append(text) # Coloco tudo em all_messages
            except Exception as e:
                continue
        
        if all_messages:
            new_message = all_messages[-1]  # Pego a ultima mensagem
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


# O que isso faz: A função main_loop() roda até ctrl+c ser ativado ou um erro acontecer, ela entra no whatsapp_web
# espera a confirmação do QR code, e então você tem que dar enter no console, ela vai digitar o nome do contact
# na caixa de busca e então apertar enter, ela faz uma chamada para a LLM, e manda a resposta inicial, então
# coloca as mensagens em uma lista, e pega apenas a ultima para mandar para a LLM e ir resolvendo essa bomba.

def main_loop():
    driver = setup_whatsapp()
    start_new_conversation(driver, "+553496724123")  # Adicione o número de telefone aqui

    # Inicializa a última mensagem com a mensagem mais recente da conversa
    last_message = read_last_message(driver)
    print(f"Última mensagem inicializada como: {last_message}") # Printando aqui so pra deixar claro o que ta rolando

    response = call_current_node()['text']
    send_message(driver, response)

    try:
        while True:
            # Ler a última mensagem
            user_input = read_last_message(driver)
            if user_input and user_input != last_message: # Isso daqui eu preciso mudar, ja que o cliente pode responder Sim,
                # sim e ainda seria uma mensagem nova.

                # Vendo o input que vem da messagem
                print(f"O input para ser processado foi: {user_input}")
                last_message = user_input
                process_user_input(user_input)

                # Chama a resposta denovo
                response = call_current_node()['text']
                send_message(driver, response)
            
            time.sleep(1)  # Aguarda 1 segundo antes de verificar novamente
    except KeyboardInterrupt:
        print("Chat interaction stopped.") # Usa Ctrl + C pra cancelar interação do bot
    finally:
        driver.quit()

if __name__ == "__main__":
    main_loop()
