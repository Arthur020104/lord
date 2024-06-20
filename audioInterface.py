import os
import time
import random
from stt.audio import play_audio
from stt.speeach_recog import escutar_e_transcrever
from lord.main import call_current_node, process_user_input
from tts.text_to_speach import text_to_speech

# Audios para existir quando nao acha o audio no banco de dados
AUDIO_FILES = [f'./Audios/waitSound ({i}).mp3' for i in range(7)]

# Pegar um audio aleatorio dos que existem, como (Um momento por favor) etc
def get_random_audio_file():
    return AUDIO_FILES[random.randint(0, len(AUDIO_FILES) - 1)]

# Função que pega o tempo gasto, usamos ela pra ver quanto que a LLM e Elevenlabs demora
def log_time_taken(task_name, start_time):
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"{task_name} took {time_taken:.2f} seconds.")
    return end_time

def main_loop():
    try:
        while True:
            start_time = time.time() # Começa a gravar o tempo
            text = call_current_node()['text'] # Da call da node atual, por exemplo conversation chain, e transforma o texto
            # em string, pq é dicionario
            log_time_taken("LLM response retrieval", start_time) # Termina gravar o tempo
            
            start_time = time.time()
            output = text_to_speech(text, audioTeste=get_random_audio_file()) # Transforma o texto que a LLM gerou em audio,
            # Utilizando API do elevenlabs, essa funcao está em text_to_speach
            log_time_taken("Text-to-Speech conversion", start_time)
            
            play_audio(output) # Da play no audio transcrito
            
            transcription = escutar_e_transcrever() # Usa o Speech to text para transformar o audio recebido em texto
            if transcription:
                print("Transcription:", transcription) 
                
            process_user_input(transcription) # Processa esse texto na LLM
    except KeyboardInterrupt:
        print("Real-time transcription stopped.")

if __name__ == "__main__":
    main_loop()
