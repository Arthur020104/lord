import speech_recognition as sr
from stt.audio import play_audio_thread
import time
from pydub import AudioSegment
def escutar_e_transcrever(audio_path='./Audios/playSound.wav'): # Funcao que pega o que ta vindo como entrada e transforma
    # em texto
    microfone = sr.Recognizer() # Reconhecer o microfone como entrada <- Provavel que vai ser aqui que vamos colocar o voip
    play_audio_thread(audio_path,0.65) # Barulho que identifica que o cara pode falar
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source) # Coisa que ajuda ambient noise
        print("Diga alguma coisa: ")
        try:
            audio = microfone.listen(source) # Ouvindo do input
        except sr.WaitTimeoutError: # Se usuario nao falar nada
            print("Não entendi")
            return 'User said nothing'
    try:
        frase = microfone.recognize_google(audio, language='pt-BR') # Mandando pro google
    except sr.UnknownValueError:
        print("User said nothing")
        return 'User said nothing'
    return frase

def convert_mp3_to_wav(mp3_file_path):
    wav_file_path = mp3_file_path.replace(".mp3", ".wav")
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(wav_file_path, format="wav")
    return wav_file_path

def transcribe_audio_file(audio_file_path):
    # Create a recognizer instance
    recognizer = sr.Recognizer()
    start_time = time.time()
    # Load the audio file
    with sr.AudioFile(audio_file_path) as audio_file:
        # Record the audio data
        audio_data = recognizer.record(audio_file)
        
        try:
            # Use Google's speech recognition to transcribe the audio
            text = recognizer.recognize_google(audio_data, language='pt-BR')
            end_time = time.time()
            print(f"Transcribed audio in {end_time - start_time} seconds")
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"


if __name__ == '__main__':
    print(transcribe_audio_file(convert_mp3_to_wav("C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/Audios/output112648.mp3"))) # Teste da função
