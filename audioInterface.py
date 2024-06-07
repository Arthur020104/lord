from stt.audio import play_audio, play_audio_thread
from stt.speeach_recog import escutar_e_transcrever
from agents.main import call_current_node, process_user_input
from tts.text_to_speach import text_to_speech
import os
import time
import random
import threading

files = [f'waitSound ({i}).mp3' for i in range(3)]

def play_wait_sound_if_slow(threshold, output_list):
    """Tocar um som de espera se output_list estiver vazio após threshold segundos."""
    time.sleep(threshold)
    if not output_list:
        play_audio_thread(files[random.randint(0, len(files) - 1)], 2)

try:
    while True:
        # Recuperar o texto do nó atual
        start_time = time.time()
        text = call_current_node()['text']
        end_time = time.time()
        text_retrieval_time = end_time - start_time
        print(f"Tempo para obter a resposta do LLM {text_retrieval_time} segundos.")
        
        # Preparar para medir o tempo de resposta do Eleven Labs
        start_time = time.time()
        output_list = []

        # Iniciar uma thread para tocar som de espera se o Eleven Labs demorar muito
        wait_thread = threading.Thread(target=play_wait_sound_if_slow, args=(1, output_list))
        wait_thread.start()

        # Chamar o Eleven Labs para converter texto em fala
        output = text_to_speech(text)
        output_list.append(output)

        # Parar a thread de som de espera se o Eleven Labs responder a tempo
        wait_thread.join()

        end_time = time.time()
        text_to_speech_time = end_time - start_time
        print(f"Tempo de resposta do Eleven Labs {text_to_speech_time} segundos.")
        
        # Tocar o áudio gerado
        play_audio(output)

        # Limpar a lista de frames
        frames = []

        # Processo de transcrição
        transcription = escutar_e_transcrever()
        
        if transcription:
            print("Transcrição:", transcription)
        
        process_user_input(transcription)

except KeyboardInterrupt:
    print("Transcrição em tempo real interrompida.")
    
