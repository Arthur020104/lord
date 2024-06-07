from stt.audio import play_audio, play_audio_thread
from stt.speeach_recog import escutar_e_transcrever
from agents.main import call_current_node, process_user_input
from tts.text_to_speach import text_to_speech
import os
import time
import random

files = []
for i in range(3):
    files.append(f'./Audios/waitSound ({i}).mp3')
frames = []
try:
    
    while True:
        start_time = time.time()
        text = call_current_node()['text']
        end_time = time.time()
        #se tiver na base de dados -> play audio
        #se nao -> chama a api
        text_retrieval_time = end_time - start_time
        print(f"Time to get LLM response {text_retrieval_time} seconds.")
        start_time = time.time()
        output = text_to_speech(text, audioTeste=files[random.randint(0,len(files)-1)])
        end_time = time.time()
        text_to_speech_time = end_time - start_time
        print(f"Eleven Labs response time {text_to_speech_time} seconds.")
        play_audio(output)
        frames = []
        #start_time = time.time()
        transcription = escutar_e_transcrever()
        #end_time = time.time()
        #print(f"Transcription completed in {end_time - start_time:.2f} seconds.")
        if transcription:
            print("Transcription:", transcription)
        #play_audio_thread(,2)
        
        process_user_input(transcription)
except KeyboardInterrupt:
    print("Real-time transcription stopped.")
    