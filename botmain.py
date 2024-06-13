import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")

    # Espera o usuário escanear o QR Code
    input("Pressione Enter após escanear o QR Code e carregar o WhatsApp Web...")
    time.sleep(10)

    return driver

def select_contact(driver, contact_name):
    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
    )
    search_box.click()
    search_box.send_keys(contact_name)
    time.sleep(0.5)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

def read_last_message(driver):
    try:
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
        all_messages = []
        for message in messages:
            try:
                message_type = message.get_attribute("class")
                if "message-in" in message_type:  # Only consider incoming messages
                    text = message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]/span').text
                    all_messages.append(text)
            except Exception as e:
                continue
        
        if all_messages:
            new_message = all_messages[-1]  # Get the latest message
            return new_message
        return None
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

def main_loop():
    driver = setup_whatsapp()
    select_contact(driver, "Marquinho")

    # Inicializa a última mensagem com a mensagem mais recente da conversa
    last_message = read_last_message(driver)
    print(f"Última mensagem inicializada como: {last_message}")

    response = call_current_node()['text']
    send_message(driver, response)

    try:
        while True:
            # Ler a última mensagem
            user_input = read_last_message(driver)
            if user_input and user_input != last_message:
                # Vendo o input
                print(f"O input para ser processado foi: {user_input}")
                last_message = user_input
                process_user_input(user_input)

                # Chama a resposta denovo
                response = call_current_node()['text']
                send_message(driver, response)
            
            time.sleep(1)  # Aguarda 1 segundo antes de verificar novamente
    except KeyboardInterrupt:
        print("Chat interaction stopped.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main_loop()