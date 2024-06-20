from datetime import datetime
import pandas as pd
import os
from datetime import datetime
from elevenlabs import save
from elevenlabs.client import ElevenLabs
import threading
from fuzzywuzzy import fuzz
from secret.elabapikey import api_key
from stt.audio import play_audio_thread

CSV_FILEPATH = './Audios/audio_text.csv' # Caminho para o CSV com os textos transcritos e o diretório do audio do respectivo
# texto.
# Inicializa o elevenlabs com a key
client = ElevenLabs(api_key=api_key)
def text_to_speech(text,audioTeste = './Audios/waitSound(0)',similarity_threshold = 0.82):

    # Aqui a unica coisa esquisita é similarity treshold, que vai de 0 até 1, ela serve para ver quão similar duas mensagens
    # são, para evitar que as vezes o tempo do elevenlabs seja muito grande

    if not os.path.exists(CSV_FILEPATH): # Criando csv se ele nao existir
        return generate_text_to_speech(text) # Aqui salvamos o texto, e o diretorio do audio
    else:
        df = pd.read_csv(CSV_FILEPATH) 

    for index, row in df.iterrows(): # Funcao que dada similaridade decide se vai ou não usar o audio com texto similar.
        max_similarity = 0
        similarity = calculate_similarity(text, row['text']) 
        if similarity > max_similarity: # Logica básica pra ver quem é o mano com maior similaridade se você nao entendeu isso
            max_similarity = similarity # vai estudar lógica de programação seu programado de python!
            texto_max = row['text']
        if max_similarity >= similarity_threshold:
            print(f"Maior similaridade e: {max_similarity} com o texto: '{texto_max}' vs o original '{text}'")
            return row['file_path'] # Se tem uma similaridade maior, retorna o path ao inves de gerar um audio
    print(f"Maior similaridade e: {max_similarity} com o texto: '{texto_max}'")
    play_audio_thread(audioTeste)
    return generate_text_to_speech(text) # Se nao achou alguem com uma boa similaridade, gera o audio

def generate_text_to_speech(text):
    current_time = datetime.now().strftime("%H%M%S") # Seed do random
    output = f'./Audios/output{current_time}.mp3'

    audio = client.generate( # Geração do audio, certeza que da pra fazer isso ser mais efetivo, tem q ler coisa do elevenlabs
        text=text,
        voice='6dHxv8ke5peKaO9xM46v', 
        model='eleven_multilingual_v2', 
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    )

    save(audio, output) # Funcao do elevenlabs pra salvar o audio pro output
    
    thread = threading.Thread(target=save_audio_and_text, args=(output, text, 1)) # Enquanto isso cria uma thread que vai salvar
    # o audio no diretório
    thread.start()

    return output

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile: # Lendo essa bomba
        return infile.read()

def save_audio_and_text(output, text, similarity_threshold = 1): # Salvando texto e o diretório dele em um csv, básico
    max_similarity = 0
    if not os.path.exists(CSV_FILEPATH):
        df = pd.DataFrame(columns=['text', 'file_path'])
        df.to_csv(CSV_FILEPATH, index=False)
        new_entry = pd.DataFrame({'text': [text], 'file_path': [output]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(CSV_FILEPATH, index=False)
        return
    else:
        df = pd.read_csv(CSV_FILEPATH)

    # Procurando por texto similar, utilizando fuzzywuzzy
    for index, row in df.iterrows():
        similarity = calculate_similarity(text, row['text'])
        if similarity > max_similarity:
            max_similarity = similarity
    if max_similarity != similarity_threshold: # Se a similaridade for diferente de 1, salva um novo texto no arquivo CSV
        new_entry = pd.DataFrame({'text': [text], 'file_path': [output]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(CSV_FILEPATH, index=False)
        return
        
def calculate_similarity(text1, text2):
    similarity = fuzz.ratio(text1, text2)/100 # o fuzzy wuzzy calcula de 0 a 100, mas queremos de 0 a 1.
    return similarity  