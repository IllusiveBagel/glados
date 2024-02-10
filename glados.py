import os
import sys
sys.path.append('./glados_tts')

from glados_tts.glados import tts_runner;
from pocketsphinx import LiveSpeech;
import speech_recognition as sr;

glados = tts_runner(False, True)

def start_up():
	glados.speak("oh, its you", True)
	print("\nWaiting for keyphrase: ")

def take_command():
    glados.speak("What do you want now?")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en')
        print(f"User said: {query}\n")
        if "hey" in query:
            query = query.replace("hey", '')
    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
    return query

start_up()

speech = LiveSpeech(
    lm=False,
    dict=os.path.join('glados.dict'),
    keyphrase='hey glados',
    kws_threshold=1e-20,
)

for phrase in speech:
    try:
        command = take_command()

        print(command)
    except Exception as e:
        print(e)