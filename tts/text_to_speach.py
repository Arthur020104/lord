from datetime import datetime
import pandas as pd
import os
from elevenlabs import save
from elevenlabs.client import ElevenLabs
import threading
from fuzzywuzzy import fuzz
from secret.elabapikey import api_key
from stt.audio import play_audio_thread

CSV_FILEPATH = './Audios/audio_text.csv'
client = ElevenLabs(api_key=api_key)

def load_audio_data():
    # Se o CSV existir, carrega os dados, caso contrário, cria um DataFrame vazio
    if os.path.exists(CSV_FILEPATH):
        return pd.read_csv(CSV_FILEPATH)
    else:
        return pd.DataFrame(columns=['text', 'file_path'])

audio_data = load_audio_data()

def text_to_speech(text, audioTeste='./Audios/waitSound(0)', similarity_threshold=0.82):
    max_similarity = 0
    best_match = None
    best_match_file = None

    # Percorre os textos no DataFrame e calcula a similaridade
    for index, row in audio_data.iterrows():
        similarity = calculate_similarity(text, row['text'])
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = row['text']
            best_match_file = row['file_path']

    # Se a maior similaridade encontrada for maior ou igual ao limiar, retorna o caminho do arquivo correspondente
    if max_similarity >= similarity_threshold:
        print(f"Best match similarity: {max_similarity} with text: '{best_match}'")
        return best_match_file

    # Imprime a maior similaridade encontrada
    print(f"Best match similarity: {max_similarity} with text: '{best_match}'")

    # Toca o áudio de espera enquanto gera um novo áudio
    play_audio_thread(audioTeste)
    return generate_text_to_speech(text)

def generate_text_to_speech(text):
    # Geração de um áudio baseado no tempo atual
    current_time = datetime.now().strftime("%H%M%S")
    output = f'./Audios/output{current_time}.mp3'

    # Gera o áudio usando ElevenLabs
    audio = client.generate(
        text=text,
        voice='6dHxv8ke5peKaO9xM46v', 
        model='eleven_multilingual_v2',
        voice_settings={
            "stability": 0.3,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True
        }
    )
    save(audio, output)
    
    # Cria uma thread para salvar o áudio e o texto no CSV
    thread = threading.Thread(target=save_audio_and_text, args=(output, text))
    thread.start()

    return output

def save_audio_and_text(output, text):
    global audio_data
    
    # Verifica se o texto já existe no DataFrame
    similarity = audio_data['text'].apply(lambda x: calculate_similarity(text, x))
    if similarity.max() < 1:
        # Se não existir, adiciona uma nova entrada ao DataFrame e salva no CSV
        new_entry = pd.DataFrame({'text': [text], 'file_path': [output]})
        audio_data = pd.concat([audio_data, new_entry], ignore_index=True)
        audio_data.to_csv(CSV_FILEPATH, index=False)

def calculate_similarity(text1, text2):
    # Calcula a similaridade entre dois textos usando fuzzywuzzy
    similarity = fuzz.token_set_ratio(text1, text2) / 100
    return similarity