from datetime import datetime
import pandas as pd
import os
from datetime import datetime
from elevenlabs import save
from elevenlabs.client import ElevenLabs
import threading
from fuzzywuzzy import fuzz

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
    
    thread = threading.Thread(target=save_audio_and_text, args=(output, text, 0.9))  # Example similarity threshold
    thread.start()

    return output

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_audio_and_text(output, text, similarity_threshold):
    csv_file = 'Audios/audio_text.csv'
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=['text', 'file_path'])
    else:
        df = pd.read_csv(csv_file)

    # Procurando por texto similar
    for index, row in df.iterrows():
        similarity = fuzz.ratio(text, row['text']) / 100.0
        if similarity >= similarity_threshold:
            return row['file_path']  # Se bateu, retorna o path do audio

    # Se nao encontrou similar, salva o texto...
    new_entry = pd.DataFrame({'text': [text], 'file_path': [output]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(csv_file, index=False)
    return 0  # 0 indica que nenhum texto foi encontrado
