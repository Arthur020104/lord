from datetime import datetime
from secret.elabapikey import api_key
import pandas as pd
import os
from datetime import datetime
from elevenlabs import save
from elevenlabs.client import ElevenLabs
import threading

# Initialize the ElevenLabs client with your API key
client = ElevenLabs(api_key=api_key)

def text_to_speech(text):
    current_time = datetime.now().strftime("%H%M%S")
    output = f'C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/Audios/output{current_time}.mp3'

    audio = client.generate(
        text=text,
        voice='7u8qsX4HQsSHJ0f8xsQZ', 
        model='eleven_multilingual_v2',
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    )
    save(audio, output)
    
    thread = threading.Thread(target=save_audio_and_text, args=(output, text))
    thread.start()

    return output

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_audio_and_text(output, text):
    csv_file = 'Audios/audio_text.csv'
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=['text', 'file_path'])
    else:
        df = pd.read_csv(csv_file)
    df = pd.concat([df, pd.DataFrame({'text': [text], 'file_path': [output]})], ignore_index=True)
    df.to_csv(csv_file, index=False)