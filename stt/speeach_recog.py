import speech_recognition as sr
from stt.audio import play_audio_thread

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

