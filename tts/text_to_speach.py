
import numpy as np
import requests
from datetime import datetime
from secret.elabapikey import api_key
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
def text_to_speech(text):
    voice_id = '7u8qsX4HQsSHJ0f8xsQZ'
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    }}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        current_time = datetime.now().strftime("%H%M%S")
        with open(f'output{current_time}.mp3', 'wb') as f:
            f.write(response.content)
        return f'C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/output{current_time}.mp3'
    else:
        print('Error:', response.text)
    