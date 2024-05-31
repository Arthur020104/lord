from stt.audio import play_audio, play_audio_thread
from stt.speeach_recog import escutar_e_transcrever
from agents.main import call_current_node, process_user_input
from tts.text_to_speach import text_to_speech
import os
import time
files = []
for i in range(3):
    files.append(f'waitSound ({i}).mp3')
frames = []
try:
    
    while True:
        start_time = time.time()
        text = call_current_node()['text']
        end_time = time.time()
        text_retrieval_time = end_time - start_time
        print(f"Text retrieved in {text_retrieval_time} seconds.")
        start_time = time.time()
        output = text_to_speech(text)
        end_time = time.time()
        text_to_speech_time = end_time - start_time
        print(f"Text to speech completed in {text_to_speech_time} seconds.")
        print('here')
        print("Output:", text)
        start_time = time.time()  
        play_audio(output)
        end_time = time.time()
        
        print(f'Audio played in {end_time - start_time:.2f} seconds.')
        frames = []
       # play_audio_thread('playSound.wav',2)
        
    
        #temp_filename = "temp.wav"
        
        # Transcribe the audio file
        start_time = time.time()
        transcription = escutar_e_transcrever()
        end_time = time.time()
        print(f"Transcription completed in {end_time - start_time:.2f} seconds.")
        if transcription:
            print("Transcription:", transcription)
        import random
        play_audio_thread(files[random.randint(0,len(files)-1)],2)
        
        process_user_input(transcription)
        #os.remove(temp_filename)

except KeyboardInterrupt:
    print("Real-time transcription stopped.")
    
