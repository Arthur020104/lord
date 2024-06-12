import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def select_contact(driver):
    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
    )
    search_box.click()
    search_box.send_keys("Marquinho")
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

def read_last_message(driver):
    try:
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]')
        last_message = messages[-1].find_element(By.XPATH, './/span[@class="_11JPr selectable-text copyable-text"]').text
        return last_message
    except Exception as e:
        print(f"Error reading last message: {e}")
        return None

def send_message(driver, message):
    try:
        message_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.click()
        message_box.send_keys(message)
        time.sleep(0.5)
        message_box.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"Error sending message: {e}")

def log_time_taken(task_name, start_time):
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"{task_name} took {time_taken:.2f} seconds.")
    return end_time

def main_loop():
    driver = setup_whatsapp()
    select_contact(driver)
    try:
        while True:
            start_time = time.time()

            # Obter resposta da LLM
            response = call_current_node()['text']

            # Enviar resposta
            send_message(driver,response)

            time.sleep(5)

            # Ler input do Usuario
            user_input = read_last_message(driver)

            # Processar input
            process_user_input(user_input)
            
            time.sleep(5)  # Aguarda 5 segundos antes de verificar novas mensagens
    except KeyboardInterrupt:
        print("Chat interaction stopped.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main_loop()
