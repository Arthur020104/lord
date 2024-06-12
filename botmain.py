import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import random
from stt.audio import play_audio, play_audio_thread
from stt.speeach_recog import escutar_e_transcrever
from agents.main import call_current_node, process_user_input
from tts.text_to_speach import text_to_speech

# Constants
AUDIO_FILES = [f'./Audios/waitSound ({i}).mp3' for i in range(3)]

def get_random_audio_file():
    return AUDIO_FILES[random.randint(0, len(AUDIO_FILES) - 1)]

def setup_whatsapp():
    
    # Inicializa o WebDriver com as opções e serviço configurados
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")

    # Espera o usuário escanear o QR Code
    input("Pressione Enter após escanear o QR Code e carregar o WhatsApp Web...")
    time.sleep(10)

    return driver

def read_last_message(driver):

    # Coleta a última mensagem recebida
    # Seleciona o contato mais recente
    recent_contact = driver.find_element(By.XPATH, '//*[@id="pane-side"]/div[1]/div/div/div[1]')
    recent_contact.click()

    # Espera o campo de mensagem estar disponível
    time.sleep(2)

    # Envia a mensagem
    message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
    message_box.send_keys('Olá, esta é uma mensagem automática.')
    message_box.send_keys(Keys.ENTER)

    #if messages:
    #    last_message = messages[-1].text
    #    return last_message
    return None

def send_message(driver, message):
    # Envia a mensagem
    message_box = driver.find_element(By.CSS_SELECTOR, 'div._3uMse')
    message_box.send_keys(message + Keys.ENTER)


def log_time_taken(task_name, start_time):
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"{task_name} took {time_taken:.2f} seconds.")
    return end_time

def main_loop():
    driver = setup_whatsapp()
    try:
        while True:
            start_time = time.time()
            
            # Ler a última mensagem
            user_input = read_last_message(driver)
            if user_input:
                print("User:", user_input)
                
                # Obter resposta da LLM
                response = call_current_node()['text']
                log_time_taken("LLM response retrieval", start_time)
                print("LLM:", response)
                
                # Enviar resposta no WhatsApp
                send_message(driver, response)
            
            time.sleep(5)  # Aguarda 5 segundos antes de verificar novas mensagens
    except KeyboardInterrupt:
        print("Chat interaction stopped.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main_loop()
