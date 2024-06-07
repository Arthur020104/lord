import os
import time
import random
from stt.audio import play_audio, play_audio_thread
from stt.speeach_recog import escutar_e_transcrever
from agents.main import call_current_node, process_user_input
from tts.text_to_speach import text_to_speech

# Constants
AUDIO_FILES = [f'./Audios/waitSound ({i}).mp3' for i in range(3)]

def get_random_audio_file():
    return AUDIO_FILES[random.randint(0, len(AUDIO_FILES) - 1)]

def log_time_taken(task_name, start_time):
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"{task_name} took {time_taken:.2f} seconds.")
    return end_time

def main_loop():
    try:
        while True:
            start_time = time.time()
            text = call_current_node()['text']
            log_time_taken("LLM response retrieval", start_time)
            
            start_time = time.time()
            output = text_to_speech(text, audioTeste=get_random_audio_file())
            log_time_taken("Text-to-Speech conversion", start_time)
            
            play_audio(output)
            
            transcription = escutar_e_transcrever()
            if transcription:
                print("Transcription:", transcription)
                
            process_user_input(transcription)
    except KeyboardInterrupt:
        print("Real-time transcription stopped.")

if __name__ == "__main__":
    main_loop()
