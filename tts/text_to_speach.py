from datetime import datetime
import pandas as pd
import os
from datetime import datetime
from elevenlabs import save
from elevenlabs.client import ElevenLabs
import threading
from fuzzywuzzy import fuzz
from secret.elabapikey import api_key
CSV_FILEPATH = 'C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/Audios/audio_text.csv'
# Initialize the ElevenLabs client with your API key
client = ElevenLabs(api_key=api_key)
def text_to_speech(text,similarity_threshold = 0.82):
    if not os.path.exists(CSV_FILEPATH):
        return generate_text_to_speech(text)
    else:
        df = pd.read_csv(CSV_FILEPATH)

    for index, row in df.iterrows():
        similarity = calculate_similarity(text, row['text'])
        if similarity >= similarity_threshold:
            return row['file_path']
    return generate_text_to_speech(text)
def generate_text_to_speech(text):
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
    
    thread = threading.Thread(target=save_audio_and_text, args=(output, text, 1))  # Example similarity threshold
    thread.start()

    return output

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_audio_and_text(output, text, similarity_threshold = 1):
    if not os.path.exists(CSV_FILEPATH):
        df = pd.DataFrame(columns=['text', 'file_path'])
        df.to_csv(CSV_FILEPATH, index=False)
        new_entry = pd.DataFrame({'text': [text], 'file_path': [output]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(CSV_FILEPATH, index=False)
        return
    else:
        df = pd.read_csv(CSV_FILEPATH)

    # Procurando por texto similar
    for index, row in df.iterrows():
        similarity = calculate_similarity(text, row['text'])
        if similarity != similarity_threshold:
            new_entry = pd.DataFrame({'text': [text], 'file_path': [output]})
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(CSV_FILEPATH, index=False)
            return
def calculate_similarity(text1, text2):
    similarity = fuzz.ratio(text1, text2)/100
    print(f"Similarity between '{text1}' and '{text2}': {similarity}")
    return similarity  