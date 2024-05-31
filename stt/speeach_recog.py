import speech_recognition as sr
from stt.audio import play_audio_thread

def escutar_e_transcrever(audio_path='playSound.wav'):
    microfone = sr.Recognizer()
    play_audio_thread(audio_path,0.65)
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)
        print("Diga alguma coisa: ")
        try:
            audio = microfone.listen(source)
        except sr.WaitTimeoutError:
            print("Não entendi")
            return ''
    try:
        frase = microfone.recognize_google(audio, language='pt-BR')
    except sr.UnknownValueError:
        print("User said nothing")
        return ''
    return frase

