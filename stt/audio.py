import pyaudio
import time
from playsound import playsound
import threading

def play_audio(file_path, delay = 1):
    time.sleep(delay)
    playsound(file_path)

def play_audio_thread(output, delay = 1):
    threading.Thread(target=play_audio, args=(output,delay)).start()